from flask import Blueprint, render_template, request, redirect, url_for, g
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, StepCard, Tag, User

help_bp = Blueprint('help', __name__)

## ヘッダーの色指定
@help_bp.before_request
def set_header_color():
    g.header_class = "header-help"

# ------------------------------------------------------------
# 新規作成
# ------------------------------------------------------------
@help_bp.route('/create', methods=['GET', 'POST'])
@login_required  # ← ログインしていないと作成できないように制限
def create_help_card():

    errors = {}
    form_data = {
        'title': '',
        'code': '',
        'message': '',
        'tags': []
    }

    if request.method == 'POST':
        # 入力値を取得
        title = request.form.get('title', '').strip()
        code = request.form.get('code', '').strip()
        message = request.form.get('message', '').strip()
        
        # フォームデータに保持（エラー時の再表示用）
        form_data['title'] = title
        form_data['code'] = code
        form_data['message'] = message

        # 🔹 タグ取得の変更点 ------------------------------------
        # HTML側が <input name="tags" value="a,b,c"> となったため、
        # getlist('tags[]') ではなく、文字列として受け取ります。
        csv_tags = request.form.get('tags', '').strip()
        
        # カンマで分割してリスト化 (空文字は除外)
        tag_names = [t for t in [x.strip() for x in csv_tags.split(',')] if t]
        
        # form_dataにはリストとして保存 (テンプレート側で join(',') して再表示するため)
        form_data['tags'] = tag_names
        # --------------------------------------------------------

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
            # エラーがある場合はテンプレートを再表示
            return render_template('help/help_card_create.html', errors=errors, form_data=form_data)

        # -------------------------------------------------------
        # 🔥 StepCard 保存
        # -------------------------------------------------------
        try:
            card = StepCard(
                title=title,
                error_code=code,
                error_message=message,
                user_id=current_user.user_id,  # ← ログイン中のユーザーIDを使用
                status='help'
            )
            db.session.add(card)
            # card.tags を操作する前に、card 自体は session に add されていればOK
            # (flush は自動で行われることが多いですが、明示的に flush しても良いです)

            # ---------------------------------------------------
            # タグ保存処理 (StepCardと同じロジック)
            # ---------------------------------------------------
            attached = set()
            for raw in tag_names:
                # タグ名の正規化（スペースをアンダースコアに）
                norm = raw.replace(' ', '_')
                
                # 重複処理（同じタグを二重登録しない）
                if norm in attached:
                    continue
                attached.add(norm)

                # 既存タグ検索（大文字小文字を区別しない）
                tag = Tag.query.filter(func.lower(Tag.tag_name) == norm.lower()).first()
                
                if not tag:
                    # 存在しなければ新規作成
                    tag = Tag(tag_name=norm)
                    db.session.add(tag)
                    db.session.flush()  # 新規タグのIDを確定させる

                # カードとタグを紐付け
                if tag not in card.tags:
                    card.tags.append(tag)

            # 最後にまとめてコミット
            db.session.commit()
            
            return redirect(url_for('help.complete'))

        except Exception as e:
            db.session.rollback()
            # ログ出力などをここに入れると良いです
            print(f"Error creating help card: {e}")
            errors['database'] = '保存中にエラーが発生しました。'
            return render_template('help/help_card_create.html', errors=errors, form_data=form_data)

    return render_template('help/help_card_create.html', errors=errors, form_data=form_data)

# ------------------------------------------------------------
# 投稿完了画面
# ------------------------------------------------------------
@help_bp.route('/complete')
def complete():
    return render_template('help/HelpCardPostComplete.html')

# ------------------------------------------------------------
# request をインポートに追加
from flask import request

# 一覧表示--------------------------------------------------------------------
@help_bp.route('/list')
def list_help_cards():
    page = request.args.get('page', 1, type=int)
    per_page = 3

    pagination = (
        StepCard.query
        .filter_by(status='help')
        .order_by(StepCard.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    return render_template('share/HelpCardShareList.html', pagination=pagination)

# ------------------------------------------------------------
# 詳細表示（コメントなし）
# ------------------------------------------------------------
@help_bp.route('/detail/no_comment/<int:card_id>')
def detail_no_comment(card_id):
    # 🔹 card_id に対応する StepCard のデータを取得
    card = StepCard.query.get_or_404(card_id) 
    
    # 🔹 取得したデータをテンプレートに渡してレンダリング
    return render_template('share/HelpCardShareDetailNoComment.html', card=card)