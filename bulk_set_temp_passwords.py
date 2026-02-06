import os
import csv
import secrets
import string

from application import application as app
from extensions import db
from models import User

# 生成する仮パスの長さ
PASSWORD_LEN = int(os.environ.get("TEMP_PASSWORD_LEN", "12"))

# 出力CSV（配布用）。実行後は安全な場所に保管して、用が済んだら削除推奨。
OUT_CSV = os.environ.get("OUT_CSV", "temp_passwords.csv")

# 既に password_hash が入っているユーザも上書きするか
FORCE_ALL = os.environ.get("FORCE_ALL", "0") == "1"


def gen_password(n: int) -> str:
    # 使う文字（見間違いしやすい文字を除外したければここを調整）
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def main():
    with app.app_context():
        # 対象ユーザを取得
        q = User.query
        if not FORCE_ALL:
            q = q.filter((User.password_hash == None) | (User.password_hash == ""))  # noqa: E711

        users = q.all()
        print(f"対象ユーザ数: {len(users)} (FORCE_ALL={FORCE_ALL})")

        if len(users) == 0:
            print("更新対象がいません。終了します。")
            return

        # CSVに「mail, organization_code, temp_password」を出す
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "mail", "organization_code", "temp_password"])

            for u in users:
                temp_pass = gen_password(PASSWORD_LEN)
                u.set_password(temp_pass)
                writer.writerow([u.user_id, u.mail, u.organization_code, temp_pass])

        db.session.commit()
        print(f"OK: password_hash を更新しました。CSV出力: {OUT_CSV}")


if __name__ == "__main__":
    main()
