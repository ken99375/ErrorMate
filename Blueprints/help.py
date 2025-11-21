from flask import Blueprint, render_template, request, redirect, url_for
from models import db, StepCard, Tag, User
from flask import g

help_bp = Blueprint('help', __name__)

## ヘッダーの色指定
@help_bp.before_request
def set_header_color():
    g.header_class = "header-help"

# ------------------------------------------------------------
# 新規作成
# ------------------------------------------------------------
@help_bp.route('/create', methods=['GET', 'POST'])
def create_help_card():

    errors = {}
    form_data = {
        'title': '',
        'code': '',
        'message': '',
        'tags': []
    }

    if request.method == 'POST':
        # 入力値を取得（エラー時に再表示するために form_data にも入れる）
        form_data['title'] = title = request.form.get('title', '').strip()
        form_data['code'] = code = request.form.get('code', '').strip()
        form_data['message'] = message = request.form.get('message', '').strip()

        # 🔹 タグ一覧（複数）を取得
        tags = request.form.getlist('tags[]')
        form_data['tags'] = tags # form_data にも保存

        # 文字数制限を定義
        MAX_TITLE = 255
        MAX_CODE = 65535
        MAX_MESSAGE = 65535

        # 必須チェック
        if not title:
            errors['title'] = 'タイトルを入力してください。'
        if not code:
            errors['code'] = 'コードを入力してください。'
        if not message:
            errors['message'] = 'メッセージを入力してください。'

        # 文字数チェック
        if title and len(title) > MAX_TITLE:
            errors['title'] = f'タイトルは{MAX_TITLE}文字以内で入力してください。'
        if code and len(code) > MAX_CODE:
            errors['code'] = f'コードは{MAX_CODE}文字以内で入力してください。'
        if message and len(message) > MAX_MESSAGE:
            errors['message'] = f'メッセージは{MAX_MESSAGE}文字以内で入力してください。'

        if errors:
            # エラーがある場合は、エラーメッセージとフォームの内容を保持してテンプレートを再表示
            return render_template('help/help_card_create.html', errors=errors, form_data=form_data)

        # -------------------------------------------------------
        # 🔥 StepCard 保存
        # -------------------------------------------------------
        card = StepCard(
            title=title,
            error_code=code,
            error_message=message,
            user_id=1,   # ←本来はログイン中のユーザーIDを入れる
            status='help'
        )
        db.session.add(card)
        db.session.commit()  # card.id を取得するためにいったんコミット

        # タグ保存処理
        for tag_name in tags:
            if not tag_name.strip():
                continue

            # 既存タグがあるか検索（tag_name が正しいフィールド）
            tag = Tag.query.filter_by(tag_name=tag_name).first()

            # 無ければ新規作成
            if not tag:
                tag = Tag(tag_name=tag_name)
                db.session.add(tag)
                db.session.commit()

            # StepCard と Tag を紐付け
            card.tags.append(tag)

        db.session.commit()

        return redirect(url_for('help.complete'))

    return render_template('help/help_card_create.html', errors=errors, form_data=form_data)

# ------------------------------------------------------------
# 投稿完了画面
# ------------------------------------------------------------
@help_bp.route('/complete')
def complete():
    return render_template('help/HelpCardPostComplete.html')

# ------------------------------------------------------------
# 一覧表示
# ------------------------------------------------------------
@help_bp.route('/list')
def list_help_cards():
    cards = StepCard.query.filter_by(status='help') \
    .order_by(StepCard.created_at.desc()) \
    .all()
    return render_template('share/HelpCardShareList.html', cards=cards)

# ------------------------------------------------------------
# 詳細表示（コメントなし）
# ------------------------------------------------------------
@help_bp.route('/detail/no_comment/<int:card_id>')
def detail_no_comment(card_id):
    # 🔹 card_id に対応する StepCard のデータを取得
    card = StepCard.query.get_or_404(card_id) 
    
    # 🔹 取得したデータをテンプレートに渡してレンダリング
    return render_template('share/HelpCardShareDetailNoComment.html', card=card)