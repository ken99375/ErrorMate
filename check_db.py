import os
import pymysql
from dotenv import load_dotenv

# .env を読み込む
load_dotenv()

# 接続設定
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        print("\n" + "="*20 + " データ確認開始 " + "="*20)

        # --- 1. ユーザーテーブル (users) ---
        print("\n[1] ユーザー一覧 (users table)")
        cursor.execute("SELECT user_id, user_name, mail, role FROM users")
        users = cursor.fetchall()
        if users:
            for u in users:
                print(f"  ID: {u['user_id']} | 名前: {u['user_name']} | Role: {u['role']} | Mail: {u['mail']}")
        else:
            print("  (データなし)")

        # --- 2. タグテーブル (tags) ---
        print("\n[2] タグ一覧 (tags table)")
        cursor.execute("SELECT tag_id, tag_name FROM tags")
        tags = cursor.fetchall()
        if tags:
            # 見やすくするためにカンマ区切りで表示
            tag_list = [f"{t['tag_id']}:{t['tag_name']}" for t in tags]
            print("  " + ", ".join(tag_list))
        else:
            print("  (データなし)")

        # --- 3. ステップカードテーブル (step_cards) ---
        print("\n[3] ステップカード一覧 (step_cards table)")
        # ユーザー名も一緒に取るために JOIN しています
        sql = """
        SELECT c.card_id, c.title, c.status, u.user_name 
        FROM step_cards c
        LEFT JOIN users u ON c.user_id = u.user_id
        """
        cursor.execute(sql)
        cards = cursor.fetchall()
        
        if cards:
            for c in cards:
                # このカードについているタグを取得
                cursor.execute("""
                    SELECT t.tag_name FROM tags t
                    JOIN card_tags ct ON t.tag_id = ct.tag_id
                    WHERE ct.card_id = %s
                """, (c['card_id'],))
                card_tags = cursor.fetchall()
                tag_names = [t['tag_name'] for t in card_tags]
                
                print(f"  ID: {c['card_id']} | 投稿者: {c['user_name']} | 状態: {c['status']}")
                print(f"     タイトル: {c['title']}")
                print(f"     タグ: {', '.join(tag_names) if tag_names else '(なし)'}")
                print("-" * 40)
        else:
            print("  (データなし)")

        # --- 4. コメントテーブル (comments) ---
        print("\n[4] コメント一覧 (comments table)")
        # 投稿者名と対象カードIDを表示
        sql = """
        SELECT cm.comment_id, cm.body, u.user_name, cm.card_id
        FROM comments cm
        LEFT JOIN users u ON cm.user_id = u.user_id
        LIMIT 100
        """
        cursor.execute(sql)
        comments = cursor.fetchall()
        
        if comments:
            for cm in comments:
                # 長いコメントは省略表示
                body_short = (cm['body'][:30] + '..') if len(cm['body']) > 30 else cm['body']
                print(f"  CardID: {cm['card_id']} | {cm['user_name']}: 「{body_short}」")
            print("  (※見やすさのため最新100件のみ表示しています)")
        else:
            print("  (データなし)")

        print("\n" + "="*20 + " 確認終了 " + "="*20 + "\n")

finally:
    conn.close()