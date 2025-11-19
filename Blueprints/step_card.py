import re
from flask import Blueprint, render_template, request, redirect, url_for,abort,session
from models import db, StepCard, User,Tag,STATUS_STEP, STATUS_PUBLIC, STATUS_DELETED
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import func
from flask import g


step_card_bp = Blueprint('step_card', __name__)

## ヘッダーの色指定
@step_card_bp.before_request
def set_header_color():
    g.header_class = "header-step"


SESSION_TTL_MIN = 1

# 一覧------------------------------------------------------------------------
@step_card_bp.route('/list')
def list_cards():
    cards = (
        StepCard.query
        .filter(StepCard.status != STATUS_DELETED)
        .filter(StepCard.status.in_((STATUS_STEP, STATUS_PUBLIC)))  
        .order_by(StepCard.created_at.desc())
        .all()
    )

    # cards = cards  :   右側cards : python側の変数名　左側card : テンプレート側に渡すときの名前
    # Python変数 cards を、テンプレートの中で cards という名前で使えるようにしてる
    
    return render_template('step_card_list.html', cards=cards)
# ---------------------------------------------------------------------------


# 詳細------------------------------------------------------------------------
@step_card_bp.route('/<int:card_id>')
def detail_card(card_id):
    card = StepCard.query.get_or_404(card_id)
    if card.status == STATUS_DELETED:
        abort(404)
    return render_template('step_card_detail.html', card=card)
# ---------------------------------------------------------------------------



# 新規作成------------------------------------------------------------------------------
@step_card_bp.route('/create', methods=['GET', 'POST'])
def create_card():

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

        # 文字数制限調節コード
        MAX_TITLE   = 255
        MAX_CODE    = 65535
        MAX_MESSAGE = 65535
        MAX_RESULT  = 65535

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
# -------------------------------------------------------------------------------------



# 完了画面
@step_card_bp.route('/create/complete')
def create_complete():
    return render_template('card/StepCardCreateComplete.html')



# 編集
@step_card_bp.route('/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    card = StepCard.query.get_or_404(card_id)

    errors = {}
    form_data = {}

    if request.method == 'POST':
        # フォーム値を取得
        title   = request.form.get('text_title', '').strip()
        error_code = request.form.get('text_error', '').strip()
        fix_code   = request.form.get('text_fixcode', '').strip()
        message    = request.form.get('text_message', '').strip()
        result     = request.form.get('text_result', '').strip()

        form_data = {
            'text_title':   title,
            'text_error':   error_code,
            'text_fixcode': fix_code,
            'text_message': message,
            'text_result':  result,
        }

        # 文字数制限調節コード
        MAX_TITLE   = 255
        MAX_CODE    = 65535
        MAX_MESSAGE = 65535
        MAX_RESULT  = 65535

        # 必須チェック
        if not title:
            errors['text_title'] = 'エラータイトルを入力してください。'
        if not error_code:
            errors['text_error'] = 'エラーコードを入力してください。'
        if not fix_code:
            errors['text_fixcode'] = '修正コードを入力してください。'
        if not message:
            errors['text_message'] = 'エラーメッセージを入力してください。'
        if not result:
            errors['text_result'] = '実装結果を入力してください。'

        # 文字数チェック
        if title and len(title) > MAX_TITLE:
            errors['text_title'] = f'エラータイトルは{MAX_TITLE}文字以内で入力してください。'
        if error_code and len(error_code) > MAX_CODE:
            errors['text_error'] = f'エラーコードは{MAX_CODE}文字以内で入力してください。'
        if fix_code and len(fix_code) > MAX_CODE:
            errors['text_fixcode'] = f'修正コードは{MAX_CODE}文字以内で入力してください。'
        if message and len(message) > MAX_MESSAGE:
            errors['text_message'] = f'エラーメッセージは{MAX_MESSAGE}文字以内で入力してください。'
        if result and len(result) > MAX_RESULT:
            errors['text_result'] = f'実装結果は{MAX_RESULT}文字以内で入力してください。'

        if errors:
            # エラーがあれば編集画面に戻す
            return render_template(
                'step_card_edit.html',
                card=card,
                errors=errors,
                form=form_data,
            )

        # 問題なければ更新
        card.title            = title
        card.error_code       = error_code
        card.modifying_code   = fix_code
        card.error_message    = message
        card.execution_result = result

        db.session.commit()
        return redirect(url_for('step_card.edit_complete'))

    # GET時
    return render_template(
        'step_card_edit.html',
        card=card,
        errors={},
        form={}
    )


@step_card_bp.route('/edit/complete')
def edit_complete():
    ## Compl"a"te ではなく、Compl"e"te！
    return render_template('card/StepCardUpdateComplete.html')



def _del_token_key(card_id: int) -> str:
    return f'delete_token:{card_id}'



# 確認画面 GET
@step_card_bp.route('/<int:card_id>/delete/confirm', methods=['GET'])
def confirm_delete(card_id):
    card = StepCard.query.get_or_404(card_id)

    # すでに削除済みなら専用画面
    if card.status == STATUS_DELETED:
        return render_template('step_card_delete_already.html', card=card)

    token = str(uuid4())
    session[_del_token_key(card_id)] = {
        'token': token,
        'exp': (datetime.utcnow() + timedelta(minutes=SESSION_TTL_MIN)).timestamp()
    }
    return render_template('step_card_delete_confirm.html', card=card, token=token)

# 論理削除 POST
@step_card_bp.route('/<int:card_id>/delete', methods=['POST'])
def delete_card(card_id):
    card = StepCard.query.get_or_404(card_id)

    # すでに削除済み
    if card.status == STATUS_DELETED:
        return render_template('step_card_delete_already.html', card=card)

    # トークン検証（セッション切れ／二重送信）
    form_token = request.form.get('delete_token', '')
    sess = session.get(_del_token_key(card_id))
    session.pop(_del_token_key(card_id), None)  # ワンタイムなので必ず破棄

    if not sess or form_token != sess.get('token'):
        # セッション切れ・無効トークン
        return render_template('step_card_delete_session_expired.html', card=card)

    if datetime.utcnow().timestamp() > sess.get('exp', 0):
        # 有効期限切れ
        return render_template('step_card_delete_session_expired.html', card=card)

    # 論理削除トライ
    try:
        card.status = STATUS_DELETED
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        # タイムアウト・DBエラー等をひとまとめに「失敗」画面
        return render_template('step_card_delete_failed.html', card=card)

    return redirect(url_for('step_card.list_cards'))



# 確認画面 
@step_card_bp.route('/<int:card_id>/share/confirm', methods=['GET'])
def confirm_share(card_id):
    card = StepCard.query.get_or_404(card_id)
    # 既に公開ならその旨を表示
    if card.status == STATUS_PUBLIC:
        return render_template('step_card_share_already.html', card=card)
    return render_template('step_card_share_confirm.html', card=card)



# 共有実行 POST（公開＋タグ保存→完了画面）
@step_card_bp.route('/<int:card_id>/share', methods=['POST'])
def do_share(card_id):
    card = StepCard.query.get_or_404(card_id)
    if card.status == STATUS_PUBLIC:
        # すでに公開なら既存の「すでに公開」画面
        return render_template('step_card_share_already.html', card=card)

    # 入力されたタグ（CSV）
    csv_tags = (request.form.get('tags') or '').strip()
    tag_names = [t for t in [x.strip() for x in csv_tags.split(',')] if t]

    if not tag_names:
        return render_template(
            'step_card_share_confirm.html',
            card=card,
            preset_tags=csv_tags,
            form_error={'tags': 'タグを1件以上入力してください'}
        )


    # タグ作成（存在しなければ新規）＋関連付け
    attached = set()
    for raw in tag_names:
        # タグ名は1つの正規化ポリシーに合わせる（小文字化＋空白を_に）
        norm = raw.replace(' ', '_')
        if norm in attached:
            continue
        attached.add(norm)

        # 既存検索（case-insensitive）
        tag = Tag.query.filter(func.lower(Tag.tag_name) == norm.lower()).first()
        if not tag:
            tag = Tag(tag_name=norm)
            db.session.add(tag)
            db.session.flush()  # id採番

        if tag not in card.tags:
            card.tags.append(tag)

    # 公開フラグに変更
    card.status = STATUS_PUBLIC

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return render_template('step_card_share_failed.html', card=card)

    # 投稿完了画面へ
    return redirect(url_for('step_card.share_post_complete'))


# 投稿完了画面
@step_card_bp.route('/share/complete', methods=['GET'])
def share_post_complete():
    return render_template('share/StepCardSharePostComplate.html')