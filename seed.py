from app import app
from models import db, User, Tag, StepCard, Comment
from datetime import datetime

def seed_data():
    """開発用の初期データを投入する"""
    with app.app_context():
        print("データベースを初期化します...")
        db.drop_all()   # 既存のテーブルを全て削除（開発用！本番では絶対ダメ）
        db.create_all() # 最新のmodels.pyに基づいてテーブルを再作成

        # --- 1. ユーザーの作成 ---
        print("ユーザーを作成中...")
        student1 = User(user_name='山田 太郎', mail='student1@test.com', password='password', role='student')
        student2 = User(user_name='鈴木 花子', mail='student2@test.com', password='password', role='student')
        teacher1 = User(user_name='佐藤 先生', mail='teacher1@test.com', password='password', role='teacher')
        
        db.session.add_all([student1, student2, teacher1])
        db.session.commit() # ユーザーIDを確定させるために一旦コミット

        # --- 2. タグの作成 ---
        print("タグを作成中...")
        tag_names = ['Python', 'Java', 'HTML/CSS', 'JavaScript', '文法エラー', '論理エラー', '環境構築']
        tags = {}
        for name in tag_names:
            tag = Tag(tag_name=name)
            db.session.add(tag)
            tags[name] = tag # 後で使いやすいように辞書に入れておく
        db.session.commit()

        # --- 3. ステップカードの作成 ---
        print("ステップカードを作成中...")
        card1 = StepCard(
            user_id=student1.user_id,
            title='PythonでNameErrorが出ます',
            error_code='print(hello)',
            error_message="NameError: name 'hello' is not defined",
            modifying_code='print("hello")',
            execution_result='hello',
            status='public'
        )

        card2 = StepCard(
            user_id=student2.user_id,
            title='Javaのセミコロン忘れ',
            error_code='System.out.println("Hello World")',
            error_message="error: ';' expected",
            modifying_code='System.out.println("Hello World");',
            execution_result='Hello World',
            status='public'
        )

        # カードをセッションに追加してからタグを紐付ける
        db.session.add_all([card1, card2])
        db.session.flush()  # IDを確定させる

        # タグ付け（カードがセッションにある状態で実行）
        card1.tags.append(tags['Python'])
        card1.tags.append(tags['文法エラー'])

        card2.tags.append(tags['Java'])
        card2.tags.append(tags['文法エラー'])

        db.session.commit()
        # --- 4. コメントの作成 ---
        print("コメントを作成中...")
        # 佐藤先生が山田くんのカードにコメント
        comment1 = Comment(
            card_id=card1.card_id,
            user_id=teacher1.user_id,
            body='文字列はクォーテーション（" または \'）で囲む必要がありますね。基本を確認しましょう！'
        )
        # 鈴木さんが山田くんのカードにコメント
        comment2 = Comment(
            card_id=card1.card_id,
            user_id=student2.user_id,
            body='私も最初よくやりました！'
        )

        db.session.add_all([comment1, comment2])
        db.session.commit()

# このブロックを追加
if __name__ == '__main__':
    seed_data()
    print("データベースシーディング完了！")