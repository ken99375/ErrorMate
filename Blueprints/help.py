# from flask import Blueprint, render_template, request, redirect, url_for

# help_bp = Blueprint('help', __name__)

# @help_bp.route('/create', methods=['GET', 'POST'])
# def create_help_card():
#         # if request.method == 'POST':
#         # # フォーム値取得（保存処理をここに追加）
#         # title = request.form.get('title')
#         # code = request.form.get('code')
#         # message = request.form.get('message')
#         # tags = request.form.get('tags')
#         # # TODO: DB 保存など
#         # return redirect(url_for('help.post_complete'))
#     return render_template('help/help_card_create.html')

from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from models import db, HelpCard, User   # ← HelpCard モデルを想定（自分のモデル名に合わせて変えてOK）

help_bp = Blueprint('help', __name__)

# ------------------------------------------------------------
# 一覧
# ------------------------------------------------------------
@help_bp.route('/list')
def list_help_cards():
    cards = (
        HelpCard.query
        .filter(HelpCard.status == 'help')
        .order_by(HelpCard.created_at.desc())
        .all()
    )
    return render_template('help/help_card_list.html', cards=cards)


# ------------------------------------------------------------
# 詳細
# ------------------------------------------------------------
@help_bp.route('/<int:card_id>')
def detail_help_card(card_id):
    card = HelpCard.query.get_or_404(card_id)
    if card.status == 'deleted':
        abort(404)
    return render_template('help/help_card_detail.html', card=card)


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
        'tags': ''
    }

    if request.method == 'POST':

        form_data['title']   = title   = request.form.get('title', '').strip()
        form_data['code']    = code    = request.form.get('code', '').strip()
        form_data['message'] = message = request.form.get('message', '').strip()
        form_data['tags']    = tags    = request.form.get('tags', '').strip()
        target = request.form.get('target', '')

        # 必須チェック
        if not title:
            errors['title'] = 'タイトルを入力してください。'
        if not code:
            errors['code'] = 'コードを入力してください。'
        if not message:
            errors['message'] = '内容を入力してください。'

        if errors:
            return render_template(
                'help/help_card_create.html',
                errors=errors,
                form_data=form_data
            )

        # 仮のユーザーID（ログイン実装前）
        user = User.query.first()

        # DB登録
        card = HelpCard(
            user_id=user.user_id if user else None,
            title=title,
            code=code,
            message=message,
            tags=tags,
            target=target,
            status='help'
        )

        db.session.add(card)
        db.session.commit()

        return redirect(url_for('help.create_complete'))

    return render_template(
        'help/help_card_create.html',
        errors=errors,
        form_data=form_data
    )

# ------------------------------------------------------------
# 新規作成 完了画面
# ------------------------------------------------------------
@help_bp.route('/create/complete')
def create_complete():
    return render_template('help/help_card_create_complete.html')


# ------------------------------------------------------------
# 編集
# ------------------------------------------------------------
@help_bp.route('/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_help_card(card_id):
    card = HelpCard.query.get_or_404(card_id)

    errors = {}
    form_data = {}

    if request.method == 'POST':
        title   = request.form.get('title', '').strip()
        code    = request.form.get('code', '').strip()
        message = request.form.get('message', '').strip()
        tags    = request.form.get('tags', '').strip()

        form_data = {
            'title': title,
            'code': code,
            'message': message,
            'tags': tags,
        }

        # 必須チェック
        if not title:
            errors['title'] = 'タイトルを入力してください。'
        if not code:
            errors['code'] = 'コードを入力してください。'
        if not message:
            errors['message'] = '内容を入力してください。'

        if errors:
            return render_template(
                'help/help_card_edit.html',
                card=card,
                errors=errors,
                form=form_data
            )

        # 更新
        card.title = title
        card.code = code
        card.message = message
        card.tags = tags

        db.session.commit()
        return redirect(url_for('help.edit_complete'))

    return render_template(
        'help/help_card_edit.html',
        card=card,
        errors={},
        form={}
    )


# ------------------------------------------------------------
# 編集完了
# ------------------------------------------------------------
@help_bp.route('/edit/complete')
def edit_complete():
    return render_template('help/help_card_edit_complete.html')
