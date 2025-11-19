# help.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, StepCard, User

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

        # 🔹 タグ一覧（配列）
        tags = request.form.getlist('tags[]')

        # 必須チェック
        if not title:
            errors['title'] = 'タイトルは必須です。'
        if not code:
            errors['code'] = 'コードは必須です。'
        if not message:
            errors['message'] = 'メッセージは必須です。'

        form_data['title'] = title
        form_data['code'] = code
        form_data['message'] = message
        form_data['tags'] = tags

        if errors:
            return render_template('help/help_card_create.html', errors=errors, form_data=form_data)

        # ----------------------------------------
        # 🔥 StepCard に保存（StepCard ではない）
        # ----------------------------------------
        card = Card(
            title=title,
            error_code=code,
            error_message=message,
            user_id=1,
            tags=",".join(tags)  # ← カンマ区切りで保存
        )

        db.session.add(card)
        db.session.commit()

        return redirect(url_for('help.list_help_cards'))

    return render_template('help/help_card_create.html', errors=errors, form_data=form_data)


# ------------------------------------------------------------
# 一覧表示
# ------------------------------------------------------------
@help_bp.route('/list')
def list_help_cards():
    cards = StepCard.query.order_by(StepCard.created_at.desc()).all()
    return render_template('help_card_list.html', cards=cards)
