# check_db.py
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError("DB接続情報が不足しています (.env の DB_HOST/DB_USER/DB_PASSWORD/DB_NAME を確認)")

def get_columns(cursor, table: str):
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    return [row["Field"] for row in cursor.fetchall()]

def pick_first_existing(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    return None

def main():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
    )

    try:
        with conn.cursor() as cursor:
            print("\n" + "=" * 24 + " DB 確認開始 " + "=" * 24)

            # --- users ---
            print("\n[1] users テーブル")
            user_cols = get_columns(cursor, "users")
            name_col = pick_first_existing(user_cols, ["username", "user_name", "name", "full_name"])
            mail_col = pick_first_existing(user_cols, ["mail", "email"])
            role_col = pick_first_existing(user_cols, ["role"])

            print(f"  検出: name_col={name_col}, mail_col={mail_col}, role_col={role_col}")

            select_cols = ["user_id"]
            if name_col: select_cols.append(name_col)
            if mail_col: select_cols.append(mail_col)
            if role_col: select_cols.append(role_col)

            cursor.execute(f"SELECT {', '.join(select_cols)} FROM users ORDER BY user_id ASC LIMIT 50")
            users = cursor.fetchall()

            if users:
                for u in users:
                    uid = u.get("user_id")
                    name = u.get(name_col) if name_col else None
                    mail = u.get(mail_col) if mail_col else None
                    role = u.get(role_col) if role_col else None
                    print(f"  ID:{uid} | name:{name} | role:{role} | mail:{mail}")
            else:
                print("  (データなし)")

            # --- tags ---
            print("\n[2] tags テーブル")
            cursor.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_id ASC LIMIT 100")
            tags = cursor.fetchall()
            if tags:
                print("  " + ", ".join([f"{t['tag_id']}:{t['tag_name']}" for t in tags]))
            else:
                print("  (データなし)")

            # --- step_cards ---
            print("\n[3] step_cards テーブル（投稿 + タグ）")
            # users の表示名（username/user_name）を JOIN で取る
            # name_col が無ければ mail を代替、それも無ければ user_id を文字で表示
            user_display_expr = None
            if name_col:
                user_display_expr = f"u.`{name_col}`"
            elif mail_col:
                user_display_expr = f"u.`{mail_col}`"
            else:
                user_display_expr = "CAST(u.user_id AS CHAR)"

            sql_cards = f"""
                SELECT c.card_id, c.title, c.status, c.user_id,
                       {user_display_expr} AS user_display
                FROM step_cards c
                LEFT JOIN users u ON c.user_id = u.user_id
                ORDER BY c.card_id DESC
                LIMIT 30
            """
            cursor.execute(sql_cards)
            cards = cursor.fetchall()

            if cards:
                for c in cards:
                    # タグ取得
                    cursor.execute("""
                        SELECT t.tag_name
                        FROM tags t
                        JOIN card_tags ct ON t.tag_id = ct.tag_id
                        WHERE ct.card_id = %s
                        ORDER BY t.tag_name ASC
                    """, (c["card_id"],))
                    card_tags = cursor.fetchall()
                    tag_names = [t["tag_name"] for t in card_tags]

                    print(f"  CardID:{c['card_id']} | 投稿者:{c.get('user_display')} | status:{c['status']}")
                    print(f"    title: {c['title']}")
                    print(f"    tags : {', '.join(tag_names) if tag_names else '(なし)'}")
                    print("-" * 42)
            else:
                print("  (データなし)")

            # status別の件数
            print("\n  [3-1] step_cards status別件数")
            cursor.execute("""
                SELECT status, COUNT(*) AS cnt
                FROM step_cards
                GROUP BY status
                ORDER BY cnt DESC
            """)
            for r in cursor.fetchall():
                print(f"   {r['status']}: {r['cnt']}")

            # --- comments ---
            print("\n[4] comments テーブル（最新100件）")
            sql_comments = f"""
                SELECT cm.comment_id, cm.card_id, cm.user_id, cm.parent_id, cm.body, cm.created_at,
                       {user_display_expr} AS user_display
                FROM comments cm
                LEFT JOIN users u ON cm.user_id = u.user_id
                ORDER BY cm.comment_id DESC
                LIMIT 100
            """
            cursor.execute(sql_comments)
            comments = cursor.fetchall()

            if comments:
                for cm in comments:
                    body = cm["body"] or ""
                    body_short = (body[:30] + "..") if len(body) > 30 else body
                    print(f"  CommentID:{cm['comment_id']} | CardID:{cm['card_id']} | {cm.get('user_display')}: 「{body_short}」"
                          f" | parent_id={cm.get('parent_id')}")
            else:
                print("  (データなし)")

            print("\n" + "=" * 24 + " 確認終了 " + "=" * 24 + "\n")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
