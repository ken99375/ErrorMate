import pymysql
import uuid
import os # 環境変数用に追加
from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_login import LoginManager, login_user, current_user, login_required
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash # パスワード生成用に追加
from werkzeug.middleware.proxy_fix import ProxyFix
from pylti.flask import lti # LTI用に追加
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
from Blueprints.lti import lti_bp

# .env読み込み
load_dotenv()

application = Flask(__name__)

# ---------------------------------------------------
# ★追加: プロキシ対応 (HTTPSとして認識させる)
# AWS ELBやCloud9の背後で動く場合に必須です
# ---------------------------------------------------

# x_proto=1 は、手前のWebサーバー(Apache/Nginx)から「httpで来てるよ」という情報を受け取る設定です
application.wsgi_app = ProxyFix(application.wsgi_app, x_proto=1, x_host=1)

# ... (既存のLTI設定) ...

application.config['LTI_CONFIG'] = {
    'secret': {
        'my_errormate_key':  os.environ['LTI_SHARED_SECRET']
    },
    'writers': {
        'grade': False,
        'submission': False
    },
    'is_secure': False  # ★重要: これを追加するとHTTPでも動きます
}

# application.config.update(
#     LTI_CONSUMER_KEY='errormate',        # Moodleに登録した値
#     LTI_SHARED_SECRET='your_secret_here' # Moodleと同じ値
# )

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
    # セキュリティ向上: 環境変数から取得するように変更推奨
    db_host = 'errormate-db.csw63pcdluwh.us-east-1.rds.amazonaws.com'
    db_user = 'admin'
    db_password = os.environ.get('MOODLE_DB_PASSWORD', 'Sukoyakana314') # .envになければデフォルト使用

    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database='moodle',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
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
        return [] 
    finally:
        # connectionが未定義の場合のエラーを防ぐ
        if 'connection' in locals() and connection.open:
            connection.close()

# ---------------------------------------------------
# コンテキストプロセッサ
# ---------------------------------------------------
@application.context_processor
def inject_notifications():
    notices = []
    if current_user.is_authenticated:
        try:
            # 注意: LTIで作成されたユーザーの user_name が Moodleの username と一致している必要があります
            notices = get_moodle_notifications(current_user.user_name)
        except Exception as e:
            print(f"Notification Error: {e}")
    return dict(notices=notices)


# ---------------------------------------------------
# LTI ログインルート (ここを追加・修正)

def lti_error(exception=None):
    print("====== LTI ERROR START ======")
    print(exception)
    print("====== LTI ERROR END ======")
    return render_template(
        'error.html',
        message="LTI認証エラーが発生しました。",
        exception=exception
    ), 500


# ② その後にルート
@application.route('/lti/launch', methods=['POST'])
# @lti(application, error=lti_error)
# def lti_launch(lti):

#     print("LTI LAUNCH CALLED")

#     moodle_user_id = lti.user_id
#     email = lti.lis_person_contact_email_primary
#     fullname = lti.lis_person_name_full or "Moodle User"
#     roles = (lti.roles or "").lower()
#     course_id = lti.context_id

#     if not moodle_user_id:
#         return "LTI user_id missing", 400

#     # --- ロール判定（ベストプラクティス） ---
#     if "instructor" in roles or "teacher" in roles:
#         role = "teacher"
#     elif "learner" in roles or "student" in roles:
#         role = "student"
#     else:
#         role = "guest"

#     # --- ユーザー取得 or 作成 ---
#     user = User.query.filter_by(moodle_user_id=moodle_user_id).first()

#     if not user:
#         user = User(
#             moodle_user_id=moodle_user_id,
#             mail=email,
#             username=fullname,
#             role=role
#         )
#         db.session.add(user)
#     else:
#         # Moodle側で名前やメールが変わることがあるので更新
#         user.mail = email
#         user.username = fullname
#         user.role = role

#     db.session.commit()

#     # --- ここ重要：セッション固定攻撃対策 ---
#     login_user(user, fresh=True)

#     print(f"LOGIN SUCCESS: {user.username} ({user.role}) from course {course_id}")

#     return redirect(url_for('main.index'))
# def lti_launch():
    
#     from flask import request
#     print("method:", request.method)
#     print("url:", request.url)
#     print("base_url:", request.base_url)
#     print("headers host:", request.headers.get("Host"))
#     print("headers x-forwarded-proto:", request.headers.get("X-Forwarded-Proto"))


#     from flask import request
#     print("===== RAW LTI POST DATA =====")
#     for k, v in request.form.items():
#         print(k, "=", v)
#     print("===== END =====")

#     return "DEBUG OK"
@lti(application, error=lti_error)
def lti_launch(lti):
    print("LTI LAUNCH VERIFIED")
    print("user_id:", lti.user_id)
    print("roles:", lti.roles)
    print("context_id:", lti.context_id)
    return redirect(url_for('main.index'))



# ---------------------------------------------------
# 自動ログインルート (廃止推奨)
# ---------------------------------------------------
# セキュリティリスクが高いため、LTI稼働後はコメントアウトまたは削除してください
# @application.route('/auto_login')
# def auto_login():
#     target_username = request.args.get('username')
#     # ... (省略) ...


# ---------------------------------------------------
# フィルタ設定・初期化
# ---------------------------------------------------
@application.template_filter('jst')
def jst(dt):
    if not dt:
        return ''
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M')

application.config.from_object(config['default'])

db.init_app(application)
migrate = Migrate(application, db)
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
application.register_blueprint(lti_bp, url_prefix='/lti')


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