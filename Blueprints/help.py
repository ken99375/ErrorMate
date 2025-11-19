from flask import Blueprint, render_template, request, redirect, url_for
from models import db, StepCard, Tag, User

help_bp = Blueprint('help', __name__)

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
        title = request.form.get('title', '')
        code = request.form.get('code', '')
        message = request.form.get('message', '')

        # 🔹 タグ一覧（複数）を取得
        tags = request.form.getlist('tags[]')

        # 必須チェック
        if not title:
            errors['title'] = 'タイトルは必須です。'
        if not code:
            errors['code'] = 'コードは必須です。'
        if not message:
            errors['message'] = 'メッセージは必須です。'

        # フォームの内容を保持
        form_data['title'] = title
        form_data['code'] = code
        form_data['message'] = message
        form_data['tags'] = tags

        if errors:
            return render_template('help_card_create.html', errors=errors, form_data=form_data)

        # -------------------------------------------------------
        # 🔥 StepCard 保存
        # -------------------------------------------------------
        card = StepCard(
            title=title,
            code=code,
            message=message,
            user_id=1   # ←本来はログイン中のユーザーIDを入れる
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

        return redirect(url_for('help.list_help_cards'))

    return render_template('help_card_create.html', errors=errors, form_data=form_data)


# ------------------------------------------------------------
# 一覧表示
# ------------------------------------------------------------
@help_bp.route('/list')
def list_help_cards():
    cards = StepCard.query.order_by(StepCard.created_at.desc()).all()
    return render_template('help_card_list.html', cards=cards)
