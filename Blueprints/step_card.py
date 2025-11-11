from flask import Blueprint, render_template, request, redirect, url_for,abort
# ★ ログイン無し運用にするので login_required / current_user は使わない
# from flask_login import login_required, current_user
from models import db, StepCard, User

step_card_bp = Blueprint('step_card', __name__)

# 一覧
@step_card_bp.route('/list')
def list_cards():
    # チーム全員共通で見せる想定なら user_id 条件は外す
    cards = (
        StepCard.query
        .filter(StepCard.status == 'step')   # ステップカードだけ
        .order_by(StepCard.created_at.desc())
        .all()
    )
    return render_template('step_card_list.html', cards=cards)

# 詳細
@step_card_bp.route('/<int:card_id>')
def detail_card(card_id):
    card = StepCard.query.get_or_404(card_id)
    # 削除済みやステップカード以外は見せないならここで制御
    if card.status == 'deleted':
        abort(404)
    return render_template('step_card_detail.html', card=card)

# 編集





# 新規作成
@step_card_bp.route('/create', methods=['GET', 'POST'])
def create_card():
    if request.method == 'POST':
        # 今は「テストユーザー1人」を仮で紐付け
        # ちゃんとやるなら User.query.first() で先頭ユーザー取ってくる
        user = User.query.first()  # 無かったらエラーになるので注意

        card = StepCard(
            user_id=user.user_id if user else None,
            title=request.form.get('text_title'),
            error_code=request.form.get('text_error'),
            modifying_code=request.form.get('text_fixcode'),
            error_message=request.form.get('text_message'),
            execution_result=request.form.get('text_result'),
            status='step',
        )
        db.session.add(card)
        db.session.commit()
        return redirect(url_for('step_card.create_complete'))

    return render_template('step_card_create.html')

# 完了画面
@step_card_bp.route('/create/complete')
def create_complete():
    return render_template('card/StepCardCreateComplate.html')
