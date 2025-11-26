import os
import pymysql
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

# 設定を取得
host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
target_db_name = os.getenv('DB_NAME')

print(f"[{host}] に接続を試みます...")

try:
    # データベース名を指定せずにサーバーに接続
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with conn.cursor() as cursor:
        # データベースを作成するSQL (日本語対応のため utf8mb4 を指定)
        sql = f"CREATE DATABASE IF NOT EXISTS {target_db_name} CHARACTER SET utf8mb4;"
        cursor.execute(sql)
        print(f"✅ データベース '{target_db_name}' の作成に成功しました！（既に存在する場合はスキップされました）")
        
        # 確認のため一覧を表示
        cursor.execute("SHOW DATABASES;")
        dbs = cursor.fetchall()
        print("\n--- 現在のデータベース一覧 ---")
        for db in dbs:
            print(f"- {db['Database']}")

    conn.close()

except Exception as e:
    print("\n❌ エラーが発生しました。")
    print("原因: .envのエンドポイントが古いか、パスワードが間違っている可能性があります。")
    print(f"エラー詳細: {e}")