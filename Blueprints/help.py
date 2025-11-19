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
        title = request.form.get('title')
        code = request.form.get('code')
        message = request.form.get('message')

        # タグ（複数）をすべて受け取る
        tags = request.form.getlist('tags[]')

        form_data['title'] = title
        form_data['code'] = code
        form_data['message'] = message
        form_data['tags'] = tags

        # バリデーション
        if not title:
            errors['title'] = 'タイトルは必須です'
        if not message:
            errors['message'] = 'メッセージは必須です'

        if errors:
            return render_template('help/help_card_create.html',
                                   form_data=form_data, errors=errors)

        # StepCard（ヘルプカード）を作成
        new_card = StepCard(
            title=title,
            code=code,
            message=message,
            status="help"  # ステータスを help として保存
        )

        # タグの処理
        for tag_name in tags:
            if not tag_name.strip():
                continue

            # 既存タグを検索
            tag = Tag.query.filter_by(tag_name=tag_name).first()
            if not tag:
                tag = Tag(tag_name=tag_name)
                db.session.add(tag)

            new_card.tags.append(tag)

        db.session.add(new_card)
        db.session.commit()

        return redirect(url_for('help.help_card_list'))

    return render_template('help/help_card_create.html',
                           form_data=form_data, errors=errors)


# ------------------------------------------------------------
# 一覧表示
# ------------------------------------------------------------
@help_bp.route('/list')
def help_card_list():
    cards = StepCard.query.filter_by(status="help").all()
    return render_template('help/help_card_list.html', cards=cards)
