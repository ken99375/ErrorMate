from flask import Blueprint, render_template, jsonify, g
from flask_login import login_required, current_user
from models import db, StepCard, Comment, Tag
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from collections import Counter

personal_bp = Blueprint('personal', __name__)

## ヘッダーの色指定
@personal_bp.before_request
def set_header_color():
    g.header_class = "header-analysis"


# エラー発生回数------------------------------------------------------------------------
@personal_bp.route('/ErrorCount', methods=['GET', 'POST'])
@login_required
def data_error_count():
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
# ★修正: URLを /api/LanguageRatio に変更して、画面表示用のURLと区別
@personal_bp.route('/api/LanguageRatio', methods=['GET', 'POST']) 
def language_ratio_data():
    user_id = current_user.user_id
    
    # 1. ユーザーのカードを全て取得
    user_cards = StepCard.query.filter_by(user_id=user_id).all()

    if not user_cards:
        return jsonify({"labels": [], "values": []})

    # 2. タグ名を集計
    # card.tags は models.py の relationship で定義された Tag オブジェクトのリストです
    all_tag_names = []
    for card in user_cards:
        for tag in card.tags:
            all_tag_names.append(tag.tag_name)
    
    # タグが一つもない場合
    if not all_tag_names:
        return jsonify({"labels": [], "values": []})

    # 3. Counterで出現回数をカウント
    tag_count = Counter(all_tag_names)

    # 4. Chart.js 用にキー(ラベル)と値(データ)をリスト化
    labels = list(tag_count.keys())
    values = list(tag_count.values())

    return jsonify({
        "labels": labels,
        "values": values
    })


# 言語種別比率 (画面表示) --------------------------------------------------------
@personal_bp.route('/LanguageRatio', methods=['GET'])
@login_required
def language_ratio_view():
    # データ存在チェック
    # ユーザーがカードを1枚でも持っているか確認
    card = StepCard.query.filter_by(user_id=current_user.user_id).first()

    # もしカードが1枚もなければ、エラー画面を表示
    if not card:
        return render_template('personal/PersonalDataError.html')

    # データがある場合は、通常のグラフ画面を表示
    return render_template('personal/PersonalDataLanguage.html')
    

# エラー種別比率------------------------------------------------------------------------
@personal_bp.route('/ErrorTypes', methods=['GET', 'POST'])
def data_error_type_ratio():
    user_id = current_user.user_id
    user_cards = StepCard.query.filter_by(user_id=user_id).all()

    if not user_cards:
        chart_data_json = json.dumps({"labels": [], "datasets": [{"data": [], "backgroundColor": []}]})
        return render_template('personal/PersonalDataErrorTypes.html', chart_data=chart_data_json)

    # エラーコード（error_code）をカウント
    error_codes = [card.error_code for card in user_cards if card.error_code]
    
    if not error_codes:
        chart_data_json = json.dumps({"labels": [], "datasets": [{"data": [], "backgroundColor": []}]})
        return render_template('personal/PersonalDataErrorTypes.html', chart_data=chart_data_json)

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