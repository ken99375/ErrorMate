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
        'tags': ''
    }

    if request.method == 'POST':

        form_data['title']   = title   = request.form.get('title', '').strip()
        form_data['code']    = code    = request.form.get('code', '').strip()
        form_data['message'] = message = request.form.get('message', '').strip()
        
        # AI で自動タグ生成した場合は ["python","Indent"] 形式で来る想定
        raw_tags = request.form.get('tags', '')
        tags_list = [t.strip() for t in raw_tags.split(',') if t.strip()]

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

        # 仮ユーザー（ログイン未実装）
        user = User.query.first()

        # ===============================
        # StepCard の作成
        # ===============================
        card = StepCard(
            user_id=user.user_id if user else None,
            title=title,
            error_code=code,
            error_message=message,
            status='help'
        )

        # ===============================
        # タグの紐付け
        # ===============================
        for tag_name in tags_list:
            tag = Tag.query.filter_by(tag_name=tag_name).first()
            if not tag:
                tag = Tag(tag_name=tag_name)
                db.session.add(tag)
            card.tags.append(tag)

        db.session.add(card)
        db.session.commit()

        return redirect(url_for('help.create_complete'))

    # GET のときはテンプレ表示
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
    return render_template('help/HelpCardPostComplate.html')
