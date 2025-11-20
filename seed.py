from application import app
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
        student3 = User(user_name='上野 優太', mail='student3@test.com', password='password', role='student')
        student4 = User(user_name='佐々木 蓮', mail='student4@test.com', password='password', role='student')
        student5 = User(user_name='中川 美咲', mail='student5@test.com', password='password', role='student')
        student6 = User(user_name='高橋 健', mail='student6@test.com', password='password', role='student')
        student7 = User(user_name='森本 彩', mail='student7@test.com', password='password', role='student')
        student8 = User(user_name='藤井 翼', mail='student8@test.com', password='password', role='student')
        student9 = User(user_name='岡本 結衣', mail='student9@test.com', password='password', role='student')
        student10 = User(user_name='清水 拓海', mail='student10@test.com', password='password', role='student')

        teacher1 = User(user_name='佐藤 先生', mail='teacher1@test.com', password='password', role='teacher')
        teacher2 = User(user_name='中村 先生', mail='teacher2@test.com', password='password', role='teacher')
        teacher3 = User(user_name='小林 先生', mail='teacher3@test.com', password='password', role='teacher')
        teacher4 = User(user_name='石田 先生', mail='teacher4@test.com', password='password', role='teacher')
        teacher5 = User(user_name='田中 先生', mail='teacher5@test.com', password='password', role='teacher')

        
        db.session.add_all([student1, student2, teacher1, teacher2, student3, student4, student5, student6, 
                            student7, student8, student9, student10, teacher3, teacher4, teacher5])
        db.session.commit() # ユーザーIDを確定させるために一旦コミット

        # --- 2. タグの作成 ---
        print("タグを作成中...")
        tag_names = ['Python', 'Java', 'HTML/CSS', 'JavaScript','文法エラー', '論理エラー', '環境構築','データベース', 'Flask', 'Django',
    'Spring Boot', 'React', 'API通信','Git/GitHub', '例外処理', 'デバッグ', '最適化', 'SQL']
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

        card3 = StepCard(
        user_id=student3.user_id,
        title='HTMLで画像が表示されない',
        error_code='<img src="img/pic.jpg">',
        error_message='ファイルパスが間違っている',
        modifying_code='<img src="images/pic.jpg">',
        execution_result='画像が正しく表示される',
        status='public'
    )

        card4 = StepCard(
        user_id=student4.user_id,
        title='JavaScriptでボタンが反応しない',
        error_code='document.getElementById("btn").onclick = testFunc;',
        error_message='関数が定義されていない',
        modifying_code='function testFunc() { alert("クリックされました"); }',
        execution_result='クリック時にアラート表示',
        status='public'
    )

        card5 = StepCard(
        user_id=student5.user_id,
        title='SQLでテーブルが見つからない',
        error_code='SELECT * FROM userss;',
        error_message='no such table: userss',
        modifying_code='SELECT * FROM users;',
        execution_result='正しくデータ取得',
        status='public'
    )


        # カードをセッションに追加してからタグを紐付ける
        db.session.add_all([card1, card2, card3, card4, card5])
        db.session.flush()  # IDを確定させる

        # タグ付け（カードがセッションにある状態で実行）
        card1.tags.append(tags['Python'])
        card1.tags.append(tags['文法エラー'])

        card2.tags.append(tags['Java'])
        card2.tags.append(tags['文法エラー'])

        card3.tags.append(tags['HTML/CSS'])
        card3.tags.append(tags['環境構築'])

        card4.tags.append(tags['JavaScript'])
        card4.tags.append(tags['論理エラー'])

        card5.tags.append(tags['データベース'])
        card5.tags.append(tags['SQL']) 

        db.session.commit()
        # --- 4. コメントの作成 ---
        print("コメントを作成中...")
        # 佐藤先生が山田くんのカードにコメント
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

        # 中村先生が鈴木さんのJavaカードにコメント
        comment3 = Comment(
            card_id=card2.card_id,
            user_id=teacher2.user_id,
            body='セミコロンの付け忘れはJavaでは頻出です。コンパイルエラーに慣れておきましょう。'
        )

        # 上野くんが鈴木さんのカードに共感コメント
        comment4 = Comment(
            card_id=card2.card_id,
            user_id=student3.user_id,
            body='自分も最近同じミスしました（笑）'
        )

        # 小林先生がHTMLカードにコメント
        comment5 = Comment(
            card_id=card3.card_id,
            user_id=teacher3.user_id,
            body='パス指定は相対パスと絶対パスの違いも理解しておくと良いです。'
        )

        # 森本さんがHTMLカードにコメント
        comment6 = Comment(
            card_id=card3.card_id,
            user_id=student7.user_id,
            body='画像フォルダ名typoでハマりました！'
        )

        # 石田先生がJavaScriptカードにコメント
        comment7 = Comment(
            card_id=card4.card_id,
            user_id=teacher4.user_id,
            body='関数宣言を定義してから呼び出す、スコープの基本も見直してみましょう。'
        )

        # 清水くんがJavaScriptカードにコメント
        comment8 = Comment(
            card_id=card4.card_id,
            user_id=student10.user_id,
            body='functionの位置を変えるだけで直るの驚きますよね。'
        )

        # 田中先生がSQLカードにコメント
        comment9 = Comment(
            card_id=card5.card_id,
            user_id=teacher5.user_id,
            body='テーブル名のtypoはよくあるので、エラーメッセージをしっかり読む癖をつけましょう。'
        )

        # 高橋さんがSQLカードにコメント
        comment10 = Comment(
            card_id=card5.card_id,
            user_id=student6.user_id,
            body='自分もuserssで詰まりました（笑）'
        )

        db.session.add_all([comment1, comment2, comment3, comment4, comment5,
    comment6, comment7, comment8, comment9, comment10])
        db.session.commit()

# このブロックを追加
if __name__ == '__main__':
    seed_data()
    print("データベースシーディング完了！")