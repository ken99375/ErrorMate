import os
from dotenv import load_dotenv

from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import timezone
from zoneinfo import ZoneInfo

import os
from flask import Flask
from dotenv import load_dotenv

# ★ .env は最初に読む（configがenv参照する可能性があるので）
load_dotenv()

from config import config
from extensions import db

application = Flask(__name__)

# ★ 先にconfigを載せる（DB URI もここで入る想定）
application.config.from_object(config["default"])

# SECRET_KEY（なければ開発用）
application.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET",
    application.config.get("SECRET_KEY", "dev-secret-key")
)

# 開発用 dev-login を使うか（auth.py 側で参照）
application.config["ENABLE_DEV_LOGIN"] = os.environ.get("ENABLE_DEV_LOGIN", "0") == "1"

# ★ 念のため：DB URI が入ってるかチェック（未設定ならここで落とす）
if not application.config.get("SQLALCHEMY_DATABASE_URI") and not application.config.get("SQLALCHEMY_BINDS"):
    raise RuntimeError("DB設定が未設定です。SQLALCHEMY_DATABASE_URI / BINDS を config または環境変数で設定してください。")

# ★ ここで初めて db をアプリに紐づける
db.init_app(application)

# ★ テーブル定義を登録（db.init_app後）
import models  # noqa: F401

# Blueprint は（できれば）この後に import/register すると事故りにくい
from Blueprints.main import main_bp
from Blueprints.auth import auth_bp
from Blueprints.step_card import step_card_bp
from Blueprints.help import help_bp
from Blueprints.personal import personal_bp
from Blueprints.share import share_bp
from Blueprints.total import total_bp
from Blueprints.api import api_bp

# ---------------------------------------------------
# プロキシ対応（必要なら）
# ---------------------------------------------------
application.wsgi_app = ProxyFix(
    application.wsgi_app,
    x_proto=1,
    x_host=1,
    x_for=1,
    x_prefix=1
)

# ---------------------------------------------------
# ミドルウェア（/errormate プレフィックス）
# ---------------------------------------------------
class PrefixMiddleware:
    def __init__(self, app, prefix=""):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ.get("PATH_INFO", "").startswith(self.prefix):
            environ["PATH_INFO"] = environ["PATH_INFO"][len(self.prefix):]
            environ["SCRIPT_NAME"] = self.prefix
            return self.app(environ, start_response)
        else:
            # /errormate 以外で来ても SCRIPT_NAME は付与しておく
            environ["SCRIPT_NAME"] = self.prefix
            return self.app(environ, start_response)

application.wsgi_app = PrefixMiddleware(application.wsgi_app, prefix="/errormate")


@application.template_filter("jst")
def jst(dt):
    """
    UTC/naiveなdatetimeを Asia/Tokyo 表示に変換して文字列化する
    """
    if not dt:
        return ""
    # naiveならUTC扱いにする（DBによりnaiveで来がち）
    if getattr(dt, "tzinfo", None) is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------
# 「notices」をテンプレに渡すだけ（Moodle通知は完全に無効化）
# ---------------------------------------------------
@application.context_processor
def inject_notifications():
    return dict(notices=[])

# ---------------------------------------------------
# DB / migrate / login
# ---------------------------------------------------
migrate = Migrate(application, db)

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "auth.login"   # Blueprint endpoint

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
    
# -----------------------------
# 403 Forbidden
# -----------------------------
@application.errorhandler(403)
def forbidden(e):
    return render_template(
        "errors/403.html",
        message="アクセス権が存在しません。ログイン状態や権限をご確認ください。"
    ), 403


# -----------------------------
# 404 Not Found
# -----------------------------
@application.errorhandler(404)
def not_found(e):
    return render_template(
        "errors/404.html",
        message="お探しのページが見つかりませんでした。URLをご確認ください。",
        path=request.path
    ), 404


# -----------------------------
# 500 Internal Server Error
# -----------------------------
@application.errorhandler(500)
def internal_error(e):
    return render_template(
        "errors/500.html",
        message="予期しないエラーが発生しました。時間をおいて再度お試しください。"
    ), 500


# -----------------------------
# 501 Not Implemented
# -----------------------------
@application.errorhandler(501)
def not_implemented(e):
    return render_template(
        "errors/501.html",
        message="この機能は現在未対応です。別の操作をお試しください。"
    ), 501

# ---------------------------------------------------
# Blueprint登録（単体運用）
# ---------------------------------------------------
application.register_blueprint(main_bp)
application.register_blueprint(step_card_bp, url_prefix="/card")
application.register_blueprint(auth_bp, url_prefix="/auth")
application.register_blueprint(help_bp, url_prefix="/help")
application.register_blueprint(personal_bp, url_prefix="/personal")
application.register_blueprint(share_bp, url_prefix="/share")
application.register_blueprint(total_bp, url_prefix="/total")
application.register_blueprint(api_bp, url_prefix="/api")

# テーブル作成（既存DBは壊さない：不足分のみ作られる）
with application.app_context():
    db.create_all()

# ---------------------------------------------------
# 起動処理
# ---------------------------------------------------
if __name__ == "__main__":
    print("--------------------------------------------------")
    print("★接続先:", application.config.get("SQLALCHEMY_DATABASE_URI"))
    print("--------------------------------------------------")
    application.run(debug=False, port=8080, host="0.0.0.0")
