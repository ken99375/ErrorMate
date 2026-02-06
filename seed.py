import os
from sqlalchemy import text

from application import application as app
from extensions import db
from models import User
import models


def bootstrap_db():
    with app.app_context():
        print("=== ErrorMate DB bootstrap (safe) ===")
        print("DB:", app.config.get("SQLALCHEMY_DATABASE_URI"))

        # 既存データを壊さず、未作成テーブルだけ作る
        # ※既存テーブルのカラム変更は行えない（それは migrate の役割）
        db.create_all()
        print("OK: db.create_all() done (no drop, no seed)")

        # 任意：username が空のユーザーだけ埋める（mailの@前）
        # 実行したい時だけ env を 1 にする
        if os.environ.get("SEED_BACKFILL_USERNAMES", "0") == "1":
            print("Running username backfill for users with NULL/empty username...")

            # RDS(MySQL)想定。mailの@より前を抽出してusernameへ。
            # usernameがNULL/空の行のみ更新するので安全。
            sql = text("""
                UPDATE users
                SET username = SUBSTRING_INDEX(mail, '@', 1)
                WHERE (username IS NULL OR username = '')
                  AND mail IS NOT NULL AND mail <> '';
            """)
            result = db.session.execute(sql)
            db.session.commit()

            # SQLAlchemyのresult.rowcountはDB/ドライバにより None の場合あり
            updated = getattr(result, "rowcount", None)
            print(f"OK: backfill done (updated={updated})")

        print("=== bootstrap finished ===")


if __name__ == "__main__":
    bootstrap_db()
