import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from sqlalchemy import func
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import db, StepCard, Tag, STATUS_PUBLIC, User, Comment, CardLike

share_bp = Blueprint('share', __name__)


# カードライブラリ（トップ）------------------------------------------------------------
@share_bp.route('/share', methods=['GET', 'POST'])
def share_card_library():
    return render_template('share/CardLibrary.html')

## ヘッダーの色指定
@share_bp.before_request
def set_header_color():
    g.header_class = "header-card"


# -------------------------------------------------------------------------
# ステップカード共有一覧 (ページネーション対応)
# -------------------------------------------------------------------------
@share_bp.route('/step_cards', methods=['GET'])
def share_step_card_list():
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

    if keywords:
        pagination = (base_q.join(StepCard.tags)
                      .filter(func.lower(Tag.tag_name).in_(keywords))
                      .distinct()
                      .paginate(page=page, per_page=per_page, error_out=False))
    else:
        pagination = base_q.paginate(page=page, per_page=per_page, error_out=False)

    # 現在のページのカードリスト
    cards = pagination.items
    card_ids = [c.card_id for c in cards]

    # いいね数集計
    like_counts = {}
    if card_ids:
        rows = (db.session.query(CardLike.card_id, func.count(CardLike.like_id))
                .filter(CardLike.card_id.in_(card_ids))
                .group_by(CardLike.card_id)
                .all())
        like_counts = {cid: cnt for cid, cnt in rows}

    # ログインユーザーのいいね状態
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
        matches=pagination,  # paginationオブジェクトを渡す
        like_counts=like_counts, 
        liked_ids=liked_ids,  
        logged_in=current_user.is_authenticated,
        login_url=url_for('auth.login', next=request.full_path or request.path),
    )


# -------------------------------------------------------------------------
# 共通いいね切り替え API (ステップカード・ヘルプカード共通)
# -------------------------------------------------------------------------
@share_bp.route('/card/<int:card_id>/like', methods=['POST'])
@login_required
def toggle_like(card_id):
    # 任意: 存在チェック
    StepCard.query.get_or_404(card_id)

    user_id = current_user.user_id
    rec = CardLike.query.filter_by(card_id=card_id, user_id=user_id).first()

    if rec:
        # すでにいいね済みなら -> 解除
        db.session.delete(rec)
        liked = False
    else:
        # まだなら -> 追加
        db.session.add(CardLike(card_id=card_id, user_id=user_id))
        liked = True

    try:
        db.session.commit()
    except IntegrityError:
        # 連打などで重複エラーが起きた場合はロールバックして「いいね済み」とみなす
        db.session.rollback()
        liked = True

    # 最新の件数を取得して返す
    count = db.session.query(func.count(CardLike.like_id)).filter_by(card_id=card_id).scalar()
    return jsonify({"liked": liked, "count": int(count)})


# -------------------------------------------------------------------------
# ステップカード詳細
# -------------------------------------------------------------------------
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


# -------------------------------------------------------------------------
# ヘルプカード共有一覧 (ページネーション対応)
# -------------------------------------------------------------------------
@share_bp.route("/help/list")
def share_help_card_list():
    page = request.args.get('page', 1, type=int)
    per_page = 9

    keyword = request.args.get("tag", "").strip()

    # ステータス 'help' で絞り込み
    query = StepCard.query.filter(StepCard.status == 'help')

    if keyword:
        tag_names = [t.strip() for t in keyword.replace(" ", " ").replace(",", " ").split() if t.strip()]
        if tag_names:
            query = query.join(StepCard.tags).filter(Tag.tag_name.in_(tag_names))

    # ページネーション実行
    pagination = query.order_by(StepCard.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    matches = pagination.items  # 現在のページのリスト

    # カードIDリスト
    card_ids = [c.card_id for c in matches]

    # いいね数集計 (CardLikeを使用)
    like_counts = {}
    if card_ids:
        rows = (db.session.query(CardLike.card_id, func.count(CardLike.like_id))
                .filter(CardLike.card_id.in_(card_ids))
                .group_by(CardLike.card_id)
                .all())
        like_counts = {cid: cnt for cid, cnt in rows}

    # ログインユーザーのいいね状態
    liked_ids = set()
    logged_in = False
    if current_user.is_authenticated:
        logged_in = True
        if card_ids:
            liked_rows = (CardLike.query.with_entities(CardLike.card_id)
                          .filter_by(user_id=current_user.user_id)
                          .filter(CardLike.card_id.in_(card_ids))
                          .all())
            liked_ids = {r.card_id for r in liked_rows}

    return render_template(
        "share/HelpCardShareList.html",
        matches=pagination, # paginationオブジェクトを渡す
        keyword=keyword,
        like_counts=like_counts,
        liked_ids=liked_ids,
        logged_in=logged_in,
    )


# -------------------------------------------------------------------------
# ヘルプカード詳細
# -------------------------------------------------------------------------
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

    roots = [c for c in comments if c.parent_id is None]
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