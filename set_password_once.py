import os
from application import application as app
from extensions import db
from models import User

TARGET_MAIL = os.environ.get("TARGET_MAIL")
NEW_PASS = os.environ.get("NEW_PASS")

if not TARGET_MAIL or not NEW_PASS:
    raise SystemExit("TARGET_MAIL と NEW_PASS を環境変数で指定してください。")

with app.app_context():
    u = User.query.filter_by(mail=TARGET_MAIL).first()
    if not u:
        raise SystemExit("ユーザが見つかりません")

    u.set_password(NEW_PASS)
    db.session.commit()
    print("OK: password set for", TARGET_MAIL)
