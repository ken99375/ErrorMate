from flask import Flask, request, session
from pylti1p3.tool_config import ToolConfDict
from pylti1p3.contrib.flask import FlaskOIDCLogin, FlaskMessageLaunch
from flask_login import LoginManager
from config import config
from models import db, User
# ★追加1：.env読み込み用のライブラリをインポート
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

# ★追加2：ここで.envファイルを強制的に読み込む！
# これがないと、configが環境変数(DB情報)を見つけられません
load_dotenv()

application = Flask(__name__)


# 現在のMoodleのIPアドレス（http:// はつけない）
MOODLE_IP = "http://54.157.54.36/"

# MoodleのURLを組み立てる
MOODLE_URL = f"http://{MOODLE_IP}"

# LTIの設定情報
lti_config = {
    # 辞書のキーも変数を使う
    MOODLE_URL: {
        "client_id": "errormate_id",
        # URLの中身も変数で自動組み立て
        "auth_login_url": f"{MOODLE_URL}/mod/lti/auth.php",
        "auth_token_url": f"{MOODLE_URL}/mod/lti/token.php",
        "key_set_url": f"{MOODLE_URL}/mod/lti/certs.php",
        "private_key_file": "private.key",
        "public_key_file": "public.key",
        "deployment_ids": ["1"]
    }
}

#  ログイン開始（OIDC Login）
@application.route('/lti/login', methods=['GET', 'POST'])
def lti_login():
    tool_conf = ToolConfDict(lti_config)
    oidc_login = FlaskOIDCLogin(request, tool_conf)
    return oidc_login.enable_check_cookies().redirect(request.args.get('target_link_uri'))
    
# 2. 実際の起動（LTI Launch）
@application.route('/lti/launch', methods=['POST'])
def lti_launch():
    tool_conf = ToolConfDict(lti_config)
    message_launch = FlaskMessageLaunch(request, tool_conf)
    
    # ここで「誰が来たか」を取得できる！
    user_data = message_launch.get_launch_data()
    email = user_data.get('email')
    name = user_data.get('name')

    # ErrorMateのログイン処理をここで行う（セッションに保存など）
    session['user_email'] = email
    
    return f"ようこそ、Moodleから来た {name} さん！"

@application.template_filter('jst')
def jst(dt):
    if not dt:
        return ''
    # DBにnaive(タイムゾーンなし)でUTC保存してる想定
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # 表示だけJSTに
    return dt.astimezone(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M')

# 設定の読み込み
application.config.from_object(config['default'])

# 接続先確認（これで mysql+pymysql://... と表示されれば成功！）
print("--------------------------------------------------") 
print("★接続先:", application.config.get('SQLALCHEMY_DATABASE_URI')) 
print("--------------------------------------------------")

# データベースの初期化
db.init_app(application)

# ログインマネージャーの初期化
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprintの登録
application.register_blueprint(main_bp)
application.register_blueprint(step_card_bp, url_prefix='/card')
application.register_blueprint(auth_bp, url_prefix='/auth')
application.register_blueprint(help_bp, url_prefix='/help')
application.register_blueprint(personal_bp, url_prefix='/personal')
application.register_blueprint(share_bp, url_prefix='/share')
application.register_blueprint(api_bp, url_prefix="/api")
application.register_blueprint(admin_bp, url_prefix='/admin')

# アプリ起動時にテーブルを作成
with application.app_context():
    db.create_all()

if __name__ == '__main__':
    # Cloud9用に、ポート8080 と ホスト0.0.0.0 を指定する
    application.run(debug=True, port=8080, host='0.0.0.0')