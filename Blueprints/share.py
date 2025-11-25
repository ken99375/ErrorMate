# share.py
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func
from flask_login import current_user
from sqlalchemy.orm import joinedload, load_only
from models import db, StepCard, Tag, STATUS_PUBLIC,User, Comment
from flask import g

share_bp = Blueprint('share', __name__)


# カードライブラリ------------------------------------------------------------
@share_bp.route('/share', methods=['GET', 'POST'])
def share_card_library():
    return render_template('share/CardLibrary.html')

## ヘッダーの色指定
@share_bp.before_request
def set_header_color():
    g.header_class = "header-card"

@share_bp.route('/share/step_cards', methods=['GET'])
def share_step_card_list():
    raw = (request.args.get('tag') or '').strip()
    keywords = [s for s in [x.strip().lower() for x in re.split(r'[,\s]+', raw)] if s]

    base_q = (
        StepCard.query
        .filter(StepCard.status == STATUS_PUBLIC)
        .options(
            # タグと作者を先読み
            joinedload(StepCard.tags).load_only(Tag.tag_id, Tag.tag_name),
            joinedload(StepCard.author).load_only(User.user_name),
            # カード側は必要な列だけ
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
        cards = (
            base_q.join(StepCard.tags)
                .filter(func.lower(Tag.tag_name).in_(keywords))
                .distinct()
                .all()
        )
    else:
        cards = base_q.all()

    return render_template(
        'share/StepCardShareList.html',
        keyword=raw,
        matches=cards,
    )


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
    # テンプレの name に合わせておく
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

# ヘルプカード共有一覧 -----------------------------------------------
@share_bp.route('/share/help_cards', methods=['GET'])
def share_help_card_list():
    raw = (request.args.get('tag') or '').strip()

    # カンマ/空白区切りのタグ検索
    keywords = [s for s in [x.strip().lower() for x in re.split(r'[,\s]+', raw)] if s]

    # help 状態のカードだけ取得
    base_q = (
        StepCard.query
        .filter(StepCard.status == 'help')
        .options(
            joinedload(StepCard.tags),   # N+1 回避
            load_only(
                StepCard.card_id, StepCard.title,
                StepCard.error_message, StepCard.created_at
            ),
        )
    )

    # タグ検索あり
    if keywords:
        q = (
            base_q.join(StepCard.tags)
            .filter(func.lower(Tag.tag_name).in_(keywords))
            .distinct()
            .order_by(StepCard.created_at.desc())
        )
        cards = q.all()
    else:
        cards = base_q.order_by(StepCard.created_at.desc()).all()

    return render_template(
        'share/HelpCardShareList.html',
        keyword=raw,
        matches=cards
    )

# ヘルプカード共有詳細 ---------------------------------------------
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
        .filter_by(card_id=card_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return render_template('share/help_card_share_detail.html', card=card, comments=comments)

