import os
from dotenv import load_dotenv

# .env を読む（USE_SQLITE / SQLITE_PATH など）
load_dotenv()

def main():
    use_sqlite = os.getenv("USE_SQLITE", "0") == "1"
    sqlite_path = os.getenv("SQLITE_PATH", "errormate_local.db")

    if not use_sqlite:
        print("❌ SQLiteモードではありません。")
        print("ローカルでSQLiteを使う場合は .env に以下を設定してください：")
        print("USE_SQLITE=1")
        print(f"SQLITE_PATH={sqlite_path}")
        raise SystemExit(1)

    # application.py の設定（config / extensions / models）を読み込んでDB初期化する
    # あなたのファイル名は application.py で、Flaskインスタンス名は application
    from application import application
    from extensions import db

    # どこにDBファイルができるか分かるように表示
    abs_db_path = os.path.abspath(sqlite_path)
    print(f"SQLiteモードでDBを作成します: {abs_db_path}")
    print("接続先:", application.config.get("SQLALCHEMY_DATABASE_URI"))

    with application.app_context():
        db.create_all()
        print("✅ SQLite のテーブル作成が完了しました。")

if __name__ == "__main__":
    main()
