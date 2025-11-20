# share.py
import re
from flask import Blueprint, render_template, request
from sqlalchemy import func
from sqlalchemy.orm import joinedload, load_only
from models import db, StepCard, Tag, STATUS_PUBLIC,User

share_bp = Blueprint('share', __name__)

# カードライブラリ
@share_bp.route('/share', methods=['GET'])
def share_card_library():
    return render_template('share/CardLibrary.html')


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
