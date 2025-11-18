# share.py
import re
from flask import Blueprint, render_template, request
from sqlalchemy import func
from sqlalchemy.orm import joinedload, load_only
from models import db, StepCard, Tag, STATUS_PUBLIC

share_bp = Blueprint('share', __name__)

# カードライブラリ
@share_bp.route('/share', methods=['GET'])
def share_card_library():
    return render_template('share/CardLibrary.html')

# ステップカード共有一覧（タグ検索）
@share_bp.route('/share/step_cards', methods=['GET'])
def share_step_card_list():
    raw = (request.args.get('tag') or '').strip()
    # カンマ/空白を区切りとして小文字化（空要素は除外）
    keywords = [s for s in [x.strip().lower() for x in re.split(r'[,\s]+', raw)] if s]

    base_q = (
        StepCard.query
        .filter(StepCard.status == STATUS_PUBLIC)
        .options(
            joinedload(StepCard.tags),  # N+1回避
            load_only(
                StepCard.card_id, StepCard.title,
                StepCard.error_message, StepCard.created_at
            ),
        )
    )

    if keywords:
        q = (
            base_q.join(StepCard.tags)
            .filter(func.lower(Tag.tag_name).in_(keywords))  # 完全一致（小文字化）
            .distinct()
            .order_by(StepCard.created_at.desc())
        )
        cards = q.all()
    else:
        cards = base_q.order_by(StepCard.created_at.desc()).all()

    return render_template(
        'share/StepCardShareList.html',
        keyword=raw,
        matches=cards,   # ← StepCardモデルのリストをそのまま渡す
    )

# ヘルプカード共有一覧
@share_bp.route('/share/help_cards', methods=['GET', 'POST'])
def share_help_card_list():
    return render_template('share/HelpCardShareList.html')