# share.py
import re
from flask import Blueprint, render_template, request
from sqlalchemy import func
from sqlalchemy.orm import joinedload, load_only
from models import db, StepCard, Tag, STATUS_PUBLIC,User
from flask import g

share_bp = Blueprint('share', __name__)

<<<<<<< HEAD

# カードライブラリ------------------------------------------------------------
@share_bp.route('/share', methods=['GET', 'POST'])
=======
# カードライブラリ
@share_bp.route('/share', methods=['GET'])
>>>>>>> 0bd337f08c98f681d2034c753e5851b47c4bbeff
def share_card_library():
    return render_template('share/CardLibrary.html')

## ヘッダーの色指定
@share_bp.before_request
def set_header_color():
    g.header_class = "header-card"

<<<<<<< HEAD
# ステップカード共有一覧------------------------------------------------------
@share_bp.route('/share/step_cards', methods=['GET'])
def share_step_card_list():
    """
    タグ検索（GET パラメータ tag を使う実装）
    実運用では step_cards を DB から取得。
    """
    keyword = request.args.get('tag', '').strip()

    # サンプルデータ（将来 DB から読み込む）
    step_cards = [
        {'id': 1, 'title': 'C言語基礎', 'tags': ['c言語', 'ポインタ', '入門']},
        {'id': 2, 'title': 'Pythonエラー集', 'tags': ['python', '例外', 'デバッグ']},
        {'id': 3, 'title': 'Flask入門', 'tags': ['python', 'flask', 'web']},
        {'id': 4, 'title': 'C言語メモ', 'tags': ['c言語', 'ビット演算']},
    ]

    matches = []
    if keyword:
        k_lower = keyword.lower()
        for card in step_cards:
            for t in card['tags']:
                if k_lower in t.lower():
                    matches.append(card)
                    break  

    return render_template('share/StepCardShareList.html',keyword=keyword,matches=matches)


# ヘルプカード共有一覧--------------------------------------------------------
@share_bp.route('/share/help_cards', methods=['GET'])
def share_help_card_list():
    keyword = request.args.get('tag', '').strip()

    # サンプルデータ（将来 DB から読み込む）
    help_cards = [
        {'id': 101, 'title': 'Python 入門', 'tags': ['python', '基礎', 'コード']},
        {'id': 102, 'title': 'Git の使い方', 'tags': ['git', 'バージョン管理', 'push']},
        {'id': 103, 'title': 'VSCode トラブルシュート', 'tags': ['vscode', '設定', 'プラグイン']},
        {'id': 104, 'title': 'Windows ショートカット', 'tags': ['windows', 'ショートカット']},
        {'id': 105, 'title': 'Windows 裏技', 'tags': ['windows', '裏技']},
    ]

    matches = []
    if keyword:
        k_lower = keyword.lower()
        for card in help_cards:
            for t in card['tags']:
                if k_lower in t.lower():
                    matches.append(card)
                    break

    return render_template('share/HelpCardShareList.html',keyword=keyword,matches=matches)
=======

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
>>>>>>> 0bd337f08c98f681d2034c753e5851b47c4bbeff
