from flask import Blueprint, render_template, jsonify, g, request
from flask_login import login_required, current_user
from models import db, StepCard, Comment, Tag
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from collections import Counter

personal_bp = Blueprint('personal', __name__,  url_prefix="/personal")

## ヘッダーの色指定
@personal_bp.before_request
def set_header_color():
    g.header_class = "header-analysis"

    # エンドポイント名 → active_key の対応
    key_map = {
        "personal.data_error_count": "errors",
        "personal.language_ratio_page": "lang",
        "personal.data_error_type_ratio": "types",
        "personal.data_comment_count": "comments",
        "personal.data_comment_trend": "trend",
    }
    g.active_key = key_map.get(request.endpoint)



# エラー発生回数------------------------------------------------------------------------
@personal_bp.route('/ErrorCount', methods=['GET', 'POST'])
@login_required
def data_error_count():
    # 現在のユーザーIDを取得
    user_id = current_user.user_id

    # --- 1. 過去7日間の日付ラベルを生成 ---
    today = datetime.utcnow().date()
    # X軸のラベル 
    date_labels = [(today - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
    # DB検索用の日付
    date_keys = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

    start_date = date_keys[0] # 7日前の日付

    # --- 2. データベースからデータを集計 (MySQL用: func.date_format) ---
    step_card_results = db.session.query(
        func.date_format(StepCard.created_at, '%Y-%m-%d').label('date'),
        func.count(StepCard.card_id)
    ).filter(
        StepCard.user_id == user_id,
        StepCard.created_at >= start_date,
        StepCard.status == 'public'
    ).group_by('date').all()
    
    # 高速で検索できるように辞書に変換
    step_counts = {date: count for date, count in step_card_results}

    # (B) HelpCard の日別カウントを取得
    help_card_results = db.session.query(
        func.date_format(StepCard.created_at, '%Y-%m-%d').label('date'),
        func.count(StepCard.card_id)
    ).filter(
        StepCard.user_id == user_id,
        StepCard.created_at >= start_date,
        StepCard.status == 'help'
    ).group_by('date').all()
    
    help_counts = {date: count for date, count in help_card_results}

    # --- 3. Chart.js用のデータ形式に整形 ---
    step_data_list = []
    help_data_list = []

    for date_key in date_keys: 
        step_data_list.append(step_counts.get(date_key, 0))
        help_data_list.append(help_counts.get(date_key, 0))

    # Chart.jsに渡す最終的なPython辞書
    chart_data_py = {
        "labels": date_labels,
        "datasets": [
            {
                "label": 'ステップカード作成数',
                "data": step_data_list,
                "borderColor": 'rgb(255, 205, 86)',
                "backgroundColor": 'rgba(255, 205, 86, 0.2)',
                "fill": True,
                "tension": 0.01
            },
            {
                "label": 'ヘルプカード作成数',
                "data": help_data_list,
                "borderColor": 'rgb(54, 162, 235)',
                "backgroundColor": 'rgba(54, 162, 235, 0.2)',
                "fill": True,
                "tension": 0.01
            }
        ]
    }
    
    chart_data_json = json.dumps(chart_data_py)

    return render_template('personal/PersonalDataErrorCount.html', chart_data=chart_data_json)


# 言語種別比率 (タグ集計) API ----------------------------------------------------

LANGUAGE_ALIASES = {
    "python": {"python", "py", "python3"},
    "java": {"java"},
    "c": {"c"},
    "c++": {"c++", "cpp"},
    "c#": {"c#", "csharp"},
    "go": {"go", "go言語", "golang"},
    "javascript": {"javascript", "js"},
    "typescript": {"typescript", "ts"},
    "php": {"php"},
    "ruby": {"ruby", "rb"},
    "swift": {"swift"},
    "kotlin": {"kotlin"},
    "rust": {"rust"}
}

def normalize_language(tag_name: str):
    tag = tag_name.lower().strip()

    for lang, aliases in LANGUAGE_ALIASES.items():
        if tag in aliases:
            return lang
    return None


# ====================================================
# 言語種別比率（画面表示）
# ====================================================
@personal_bp.route("/language_ratio")
@login_required
def language_ratio_page():
    return render_template("personal/PersonalDataLanguage.html")


@personal_bp.route('/api/language_ratio')
@login_required
def language_ratio_api():
    from collections import Counter

    user_id = current_user.user_id
    cards = StepCard.query.filter_by(user_id=user_id).all()

    counter = Counter()

    for card in cards:
        for tag in card.tags:
            normalized = normalize_language(tag.tag_name)
            if normalized:
                counter[normalized] += 1

    return jsonify(counter)

    

# エラー種別比率------------------------------------------------------------------------
@personal_bp.route('/ErrorTypes', methods=['GET', 'POST'])
@login_required
def data_error_type_ratio():
    user_id = current_user.user_id
    user_cards = StepCard.query.filter_by(user_id=user_id).all()

    if not user_cards:
        chart_data_json = json.dumps({"labels": [], "datasets": [{"data": [], "backgroundColor": []}]})
        return render_template('personal/PersonalDataErrorTypes.html',
                               active_key='types',
                               chart_data=chart_data_json)

    error_codes = [card.error_code for card in user_cards if card.error_code]

    if not error_codes:
        chart_data_json = json.dumps({"labels": [], "datasets": [{"data": [], "backgroundColor": []}]})
        return render_template('personal/PersonalDataErrorTypes.html',
                               active_key='types',
                               chart_data=chart_data_json)

    error_count = Counter(error_codes)

    # 色パレット
    colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
    ]

    # Chart.js用のデータ形式に整形
    chart_data_py = {
        "labels": list(error_count.keys()),
        "datasets": [
            {
                "data": list(error_count.values()),
                "backgroundColor": colors[:len(error_count)],
                "borderColor": 'rgba(255, 255, 255, 1)',
                "borderWidth": 2
            }
        ]
    }
    
    chart_data_json = json.dumps(chart_data_py)

    return render_template('personal/PersonalDataErrorTypes.html', chart_data=chart_data_json)


# コメント回数------------------------------------------------------------------------
@personal_bp.route('/Comment', methods=['GET', 'POST'])
@login_required
def data_comment_count():
    user_id = current_user.user_id
    
    # --- 1. 過去7日間の日付ラベルを生成 ---
    today = datetime.utcnow().date()
    date_labels = [(today - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
    date_keys = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

    start_date = date_keys[0]  # 7日前の日付

    # --- 2. データベースからコメント数を集計 (MySQL用: func.date_format) ---
    comment_results = db.session.query(
        func.date_format(Comment.created_at, '%Y-%m-%d').label('date'),
        func.count(Comment.comment_id)
    ).filter(
        Comment.user_id == user_id,
        Comment.created_at >= start_date
    ).group_by('date').all()
    
    comment_counts = {date: count for date, count in comment_results}

    # --- 3. Chart.js用のデータ形式に整形 ---
    comment_data_list = []

    for date_key in date_keys:
        comment_data_list.append(comment_counts.get(date_key, 0))

    chart_data_py = {
        "labels": date_labels,
        "datasets": [
            {
                "label": 'コメント数',
                "data": comment_data_list,
                "borderColor": 'rgb(75, 192, 192)',
                "backgroundColor": 'rgba(75, 192, 192, 0.2)',
                "fill": True,
                "tension": 0.4,
                "borderWidth": 2
            }
        ]
    }
    
    chart_data_json = json.dumps(chart_data_py)

    return render_template('personal/PersonalDataComment.html', chart_data=chart_data_json)


# コメント傾向------------------------------------------------------------------------
@personal_bp.route('/Trend', methods=['GET', 'POST'])
@login_required
def data_comment_trend():
    user_id = current_user.user_id
    
    # --- 2. 送ったコメント数を集計 ---
    sent_comments = db.session.query(
        func.count(Comment.comment_id)
    ).filter(
        Comment.user_id == user_id
    ).scalar() or 0
    
    # --- 3. 受け取ったコメント数を集計 ---
    # StepCard.user_id が現在ユーザーで、そのカードに対するコメント
    received_comments = db.session.query(
        func.count(Comment.comment_id)
    ).join(StepCard, Comment.card_id == StepCard.card_id).filter(
        StepCard.user_id == user_id
    ).scalar() or 0
    
    # --- 4. Chart.js用のデータ形式に整形 ---
    chart_data_py = {
        "labels": ['送ったコメント', '受け取ったコメント'],
        "datasets": [
            {
                "data": [sent_comments, received_comments],
                "backgroundColor": [
                    'rgba(255, 99, 132, 0.8)',   # 送ったコメント（赤）
                    'rgba(54, 162, 235, 0.8)'    # 受け取ったコメント（青）
                ],
                "borderColor": 'rgba(255, 255, 255, 1)',
                "borderWidth": 2
            }
        ]
    }
    
    chart_data_json = json.dumps(chart_data_py)

    return render_template('personal/PersonalDataTrend.html', chart_data=chart_data_json)
    
    
@personal_bp.context_processor
def inject_active_key():
    return {"active_key": getattr(g, "active_key", None)}

