import pymysql
from flask import Flask, request, session, redirect, url_for, render_template
from flask_login import LoginManager, login_user, current_user, login_required
from config import config
from models import db, User
from dotenv import load_dotenv
from datetime import timezone
from zoneinfo import ZoneInfo

# Blueprintのインポート
from Blueprints.main import main_bp
from Blueprints.auth import auth_bp
from Blueprints.step_card import step_card_bp
from Blueprints.help import help_bp
from Blueprints.personal import personal_bp
from Blueprints.share import share_bp
from Blueprints.api import api_bp
from Blueprints.admin import admin_bp

# .env読み込み
load_dotenv()

application = Flask(__name__)

# ---------------------------------------------------
# ミドルウェア（URL修正用）
# ---------------------------------------------------
class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)

application.wsgi_app = PrefixMiddleware(application.wsgi_app, prefix='/errormate')

# ---------------------------------------------------
# Moodle通知取得関数
# ---------------------------------------------------
def get_moodle_notifications(username):
    # MoodleのDB接続情報
    connection = pymysql.connect(
        host='errormate-db.csw63pcdluwh.us-east-1.rds.amazonaws.com',
        user='admin',
        password='Sukoyakana314',
        database='moodle',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            # SQL: ErrorMateのusernameとMoodleのusernameが一致する前提
            sql = """
            SELECT n.subject, n.smallmessage, n.timecreated
            FROM mdl_notifications n
            JOIN mdl_user u ON n.useridto = u.id
            WHERE u.username = %s
            AND n.timeread IS NULL
            ORDER BY n.timecreated DESC
            LIMIT 5
            """
            cursor.execute(sql, (username,))
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(f"Moodle DB Error: {e}")
        return [] # エラー時は空リストを返す
    finally:
        connection.close()

# ---------------------------------------------------
# コンテキストプロセッサ（全ページで通知変数を使えるようにする魔法）
# ---------------------------------------------------
@application.context_processor
def inject_notifications():
    notices = []
    # ログインしている時だけMoodleを見に行く
    if current_user.is_authenticated:
        try:
            # Userモデルのカラム名に合わせて修正 (user_name or name or username)
            # auto_loginの記述を見ると 'user_name' のようです
            notices = get_moodle_notifications(current_user.user_name)
        except Exception as e:
            print(f"Notification Error: {e}")
    
    # これでHTML側では {{ notices }} と書くだけで表示されます
    return dict(notices=notices)


# ---------------------------------------------------
# 自動ログインルート
# ---------------------------------------------------
@application.route('/auto_login')
def auto_login():
    target_username = request.args.get('username')
    if not target_username:
        return "エラー: ユーザー名が指定されていません"

    user = User.query.filter_by(user_name=target_username).first()

    if user:
        login_user(user)
        return redirect(url_for('main.index')) # Blueprintの場合は 'main.index'
    else:
        return f"エラー: ユーザー '{target_username}' はシステムに登録されていません。"

# ---------------------------------------------------
# フィルタ設定
# ---------------------------------------------------
@application.template_filter('jst')
def jst(dt):
    if not dt:
        return ''
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M')

# 設定読み込み
application.config.from_object(config['default'])

# DB初期化
db.init_app(application)

# ログインマネージャー初期化
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprint登録
application.register_blueprint(main_bp)
application.register_blueprint(step_card_bp, url_prefix='/card')
application.register_blueprint(auth_bp, url_prefix='/auth')
application.register_blueprint(help_bp, url_prefix='/help')
application.register_blueprint(personal_bp, url_prefix='/personal')
application.register_blueprint(share_bp, url_prefix='/share')
application.register_blueprint(api_bp, url_prefix='/api')
application.register_blueprint(admin_bp, url_prefix='/admin')

# テーブル作成
with application.app_context():
    db.create_all()

# ---------------------------------------------------
# 起動処理
# ---------------------------------------------------
if __name__ == '__main__':
    print("--------------------------------------------------") 
    print("★接続先:", application.config.get('SQLALCHEMY_DATABASE_URI')) 
    print("--------------------------------------------------")
    application.run(debug=True, port=8080, host='0.0.0.0')