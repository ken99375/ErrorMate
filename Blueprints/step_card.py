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




# 新規作成
@step_card_bp.route('/create', methods=['GET', 'POST'])
def create_card():
    from models import User  # まだ上でimportしてなければ追加

    errors = {}
    form_data = {
        'text_title': '',
        'text_error': '',
        'text_fixcode': '',
        'text_message': '',
        'text_result': '',
    }

    if request.method == 'POST':
        # 入力値を取得（エラー時に再表示するために form_data にも入れる）
        form_data['text_title']   = title   = request.form.get('text_title', '').strip()
        form_data['text_error']   = error   = request.form.get('text_error', '').strip()
        form_data['text_fixcode'] = fixcode = request.form.get('text_fixcode', '').strip()
        form_data['text_message'] = msg     = request.form.get('text_message', '').strip()
        form_data['text_result']  = result  = request.form.get('text_result', '').strip()

        # 上限値（設計に合わせて調整して）
        MAX_TITLE   = 255
        MAX_CODE    = 4000
        MAX_MESSAGE = 4000
        MAX_RESULT  = 4000

        # 必須チェック
        if not title:
            errors['text_title'] = 'エラータイトルを入力してください。'
        if not error:
            errors['text_error'] = 'エラーコードを入力してください。'
        if not fixcode:
            errors['text_fixcode'] = '修正コードを入力してください。'
        if not msg:
            errors['text_message'] = 'エラーメッセージを入力してください。'
        if not result:
            errors['text_result'] = '実装結果を入力してください。'

        # 文字数チェック
        if title and len(title) > MAX_TITLE:
            errors['text_title'] = f'エラータイトルは{MAX_TITLE}文字以内で入力してください。'
        if error and len(error) > MAX_CODE:
            errors['text_error'] = f'エラーコードは{MAX_CODE}文字以内で入力してください。'
        if fixcode and len(fixcode) > MAX_CODE:
            errors['text_fixcode'] = f'修正コードは{MAX_CODE}文字以内で入力してください。'
        if msg and len(msg) > MAX_MESSAGE:
            errors['text_message'] = f'エラーメッセージは{MAX_MESSAGE}文字以内で入力してください。'
        if result and len(result) > MAX_RESULT:
            errors['text_result'] = f'実装結果は{MAX_RESULT}文字以内で入力してください。'

        # エラーがあれば保存せず画面再表示
        if errors:
            return render_template('step_card_create.html',errors=errors,form_data=form_data)

        # ここまで来たらDB保存
        user = User.query.first()  # いまは仮で先頭ユーザー
        card = StepCard(
            user_id=user.user_id if user else None,
            title=title,
            error_code=error,
            modifying_code=fixcode,
            error_message=msg,
            execution_result=result,
            status='step',
        )
        db.session.add(card)
        db.session.commit()

        return redirect(url_for('step_card.create_complete'))

    # GET のとき
    return render_template('step_card_create.html',errors=errors,form_data=form_data)

# 完了画面
@step_card_bp.route('/create/complete')
def create_complete():
    return render_template('card/StepCardCreateComplate.html')
