import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from sqlalchemy import func
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload, load_only
from models import db, StepCard, Tag, STATUS_PUBLIC, User, Comment, CardLike # HelpLikeが必要なら追加、無ければCardLikeに統一
from flask import session

share_bp = Blueprint('share', __name__)


# カードライブラリ------------------------------------------------------------
@share_bp.route('/share', methods=['GET', 'POST'])
def share_card_library():
    return render_template('share/CardLibrary.html')

## ヘッダーの色指定
@share_bp.before_request
def set_header_color():
    g.header_class = "header-card"


# ステップカード共有一覧 (ページネーション追加)
@share_bp.route('/step_cards', methods=['GET'])
def share_step_card_list():
    # ★追加: ページ番号と件数設定
    page = request.args.get('page', 1, type=int)
    per_page = 9

    raw = (request.args.get('tag') or '').strip()
    keywords = [s for s in [x.strip().lower() for x in re.split(r'[,\s]+', raw)] if s]

    base_q = (
        StepCard.query
        .filter(StepCard.status == STATUS_PUBLIC)
        .options(
            joinedload(StepCard.tags).load_only(Tag.tag_id, Tag.tag_name),
            joinedload(StepCard.author).load_only(User.user_name),
            load_only(
                StepCard.card_id,
                StepCard.title,
                StepCard.error_message,
                StepCard.created_at,
            ),
        )
        .order_by(StepCard.created_at.desc())
    )

    # ★修正: .all() ではなく .paginate() を使用
    if keywords:
        pagination = (base_q.join(StepCard.tags)
                      .filter(func.lower(Tag.tag_name).in_(keywords))
                      .distinct()
                      .paginate(page=page, per_page=per_page, error_out=False))
    else:
        pagination = base_q.paginate(page=page, per_page=per_page, error_out=False)

    # ロジック計算用に現在のページのリストを取り出す
    cards = pagination.items

    card_ids = [c.card_id for c in cards]

    like_counts = {}
    if card_ids:
        rows = (db.session.query(CardLike.card_id, func.count(CardLike.like_id))
                .filter(CardLike.card_id.in_(card_ids))
                .group_by(CardLike.card_id)
                .all())
        like_counts = {cid: cnt for cid, cnt in rows}

    liked_ids = set()
    if getattr(current_user, 'is_authenticated', False) and card_ids:
        liked_rows = (CardLike.query.with_entities(CardLike.card_id)
                      .filter_by(user_id=current_user.user_id)
                      .filter(CardLike.card_id.in_(card_ids))
                      .all())
        liked_ids = {r.card_id for r in liked_rows}

    return render_template(
        'share/StepCardShareList.html',
        keyword=raw,
        matches=pagination,  # ★修正: リスト(cards)ではなくpaginationオブジェクトを渡す
        like_counts=like_counts, 
        liked_ids=liked_ids,  
        logged_in=current_user.is_authenticated,
        login_url=url_for('auth.login', next=request.full_path or request.path),
    )


@share_bp.route('/card/<int:card_id>/like', methods=['POST'])
@login_required
def toggle_like(card_id):
    # 任意: 存在チェック
    StepCard.query.get_or_404(card_id)

    rec = CardLike.query.filter_by(card_id=card_id, user_id=current_user.user_id).first()
    if rec:
        db.session.delete(rec)
        liked = False
    else:
        db.session.add(CardLike(card_id=card_id, user_id=current_user.user_id))
        liked = True
    db.session.commit()

    count = db.session.query(func.count(CardLike.like_id)).filter_by(card_id=card_id).scalar()
    return jsonify({"liked": liked, "count": int(count)})


@share_bp.route('/card/<int:card_id>', methods=['GET'])
def share_card_detail(card_id):
    card = (
        StepCard.query
        .options(joinedload(StepCard.author), joinedload(StepCard.tags))
        .filter(StepCard.card_id == card_id, StepCard.status == STATUS_PUBLIC)
        .first_or_404()
    )

    comments = (
        Comment.query
        .options(joinedload(Comment.author))
        .filter_by(card_id=card_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    roots = [c for c in comments if c.parent_id is None]
    replies_map = {}
    for c in comments:
        if c.parent_id:
            replies_map.setdefault(c.parent_id, []).append(c)
    # 返信を時刻昇順に
    for lst in replies_map.values():
        lst.sort(key=lambda x: x.created_at)

    return render_template(
        'share/step_card_share_detail.html',
        card=card,
        roots=roots,
        replies_map=replies_map,
    )

@share_bp.route('/card/<int:card_id>/comment', methods=['POST'])
def post_comment(card_id):
    body = (request.form.get('body') or '').strip()
    parent_id_raw = request.form.get('parent_id')
    parent_id = int(parent_id_raw) if parent_id_raw else None

    if not body:
        return redirect(url_for('share.share_card_detail', card_id=card_id))

    uid = current_user.user_id if getattr(current_user, 'is_authenticated', False) else 1

    c = Comment(card_id=card_id, user_id=uid, body=body, parent_id=parent_id)
    db.session.add(c)
    db.session.commit()
    return redirect(url_for('share.share_card_detail', card_id=card_id))


# ヘルプカード共有一覧 (ページネーション追加) -----------------------------------------------
@share_bp.route("/help/list")
def share_help_card_list():
    # ★追加: ページ番号設定
    page = request.args.get('page', 1, type=int)
    per_page = 9

    keyword = request.args.get("tag", "").strip()

    # ① カードを取得
    query = StepCard.query.filter(StepCard.status == 'help') # ステータスで絞り込みを明示

    if keyword:
        tag_names = [t.strip() for t in keyword.replace(" ", " ").replace(",", " ").split() if t.strip()]
        if tag_names:
            query = query.join(StepCard.tags).filter(Tag.tag_name.in_(tag_names))

    # ★修正: .all() ではなく .paginate() を使用
    pagination = query.order_by(StepCard.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # リスト本体を取り出す
    matches = pagination.items

    # ② いいね数を集計
    # ※注意: もし HelpLike モデルがない場合は CardLike に修正してください
    # ここでは元のコードにあった HelpLike をそのまま残していますが、エラーになる場合は CardLike に変えてください
    try:
        from models import HelpLike
        like_counts = {
            card.card_id: HelpLike.query.filter_by(help_id=card.card_id).count()
            for card in matches
        }
    except ImportError:
        # HelpLikeがない場合のフォールバック（CardLikeを使う想定）
        like_counts = {
            card.card_id: CardLike.query.filter_by(card_id=card.card_id).count()
            for card in matches
        }

    # ③ ログインユーザの「いいね済みカード」
    liked_ids = set()
    logged_in = False
    if "user_id" in session:
        user_id = session["user_id"]
        logged_in = True
        
        try:
            from models import HelpLike
            liked_ids = {
                like.help_id for like in HelpLike.query.filter_by(user_id=user_id).all()
            }
        except ImportError:
             liked_ids = {
                like.card_id for like in CardLike.query.filter_by(user_id=user_id).filter(CardLike.card_id.in_([c.card_id for c in matches])).all()
            }

    # ④ テンプレートに渡す
    return render_template(
        "share/HelpCardShareList.html",
        matches=pagination, # ★修正: paginationオブジェクトを渡す
        keyword=keyword,
        like_counts=like_counts,
        liked_ids=liked_ids,
        logged_in=logged_in,
    )


@share_bp.route('/share/help_card/<int:card_id>', methods=['GET'])
def share_help_card_detail(card_id):
    card = (
        StepCard.query
        .options(joinedload(StepCard.author), joinedload(StepCard.tags))
        .filter(StepCard.card_id == card_id, StepCard.status == 'help')
        .first_or_404()
    )

    comments = (
        Comment.query
        .options(joinedload(Comment.author))
        .filter_by(card_id=card_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    # 親コメント
    roots = [c for c in comments if c.parent_id is None]

    # 子コメントの辞書
    replies_map = {}
    for c in comments:
        if c.parent_id:
            replies_map.setdefault(c.parent_id, []).append(c)

    return render_template(
        'share/help_card_share_detail.html',
        card=card,
        roots=roots,
        replies_map=replies_map
    )

@share_bp.route('/share/help_card/<int:card_id>/comment', methods=['POST'])
def post_help_comment(card_id):
    body = (request.form.get('body') or '').strip()
    parent_id_raw = request.form.get('parent_id')
    parent_id = int(parent_id_raw) if parent_id_raw else None

    if not body:
        return redirect(url_for('share.share_help_card_detail', card_id=card_id))

    uid = current_user.user_id if getattr(current_user, 'is_authenticated', False) else 1

    c = Comment(
        card_id=card_id,
        user_id=uid,
        body=body,
        parent_id=parent_id
    )

    db.session.add(c)
    db.session.commit()

    return redirect(url_for('share.share_help_card_detail', card_id=card_id))
    
@share_bp.route("/help/<int:card_id>/like", methods=["POST"])
def help_like(card_id):
    if "user_id" not in session:
        return jsonify({"error": "login_required"}), 401

    user_id = session["user_id"]

    # ※ここもHelpLikeがない場合はCardLikeに修正が必要です
    try:
        from models import HelpLike
        like = HelpLike.query.filter_by(user_id=user_id, help_id=card_id).first()
    except ImportError:
        # HelpLikeがインポートできない場合の仮実装（CardLike）
        # 実際にはmodels.pyに合わせてどちらか一方に統一してください
        return jsonify({"error": "Configuration Error"}), 500

    if like:
        db.session.delete(like)
        db.session.commit()
        liked = False
    else:
        new_like = HelpLike(user_id=user_id, help_id=card_id)
        db.session.add(new_like)
        db.session.commit()
        liked = True

    count = HelpLike.query.filter_by(help_id=card_id).count()

    return jsonify({"liked": liked, "count": count})