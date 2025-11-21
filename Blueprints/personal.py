from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required
from models import db, StepCard # 1. モデルをインポート
from sqlalchemy import func                # 2. SQL関数をインポート
from datetime import datetime, timedelta   # 3. 日付操作をインポート
import json                                # 4. JSONをインポート
from flask_login import current_user
from collections import Counter
from flask import g

personal_bp = Blueprint('personal', __name__)

## ヘッダーの色指定
@personal_bp.before_request
def set_header_color():
    g.header_class = "header-analysis"


# エラー発生回数------------------------------------------------------------------------
@personal_bp.route('/ErrorCount', methods=['GET', 'POST'])
def data_error_count():

    # --- 1. 過去7日間の日付ラベルを生成 ---
    today = datetime.utcnow().date()
    # X軸のラベル 
    date_labels = [(today - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
    # DB検索用の日付
    date_keys = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

    start_date = date_keys[0] # 7日前の日付

    # --- 2. データベースからデータを集計 ---
    step_card_results = db.session.query(
    func.strftime('%Y-%m-%d', StepCard.created_at).label('date'),
    func.count(StepCard.card_id)
    ).filter(
        StepCard.created_at >= start_date,
        StepCard.status == 'public'
    ).group_by('date').all()
    # 高速で検索できるように辞書に変換 (例: {'2025-11-18': 5})
    step_counts = {date: count for date, count in step_card_results}

    # (B) HelpCard の日別カウントを取得
    help_card_results = db.session.query(
    func.strftime('%Y-%m-%d', StepCard.created_at).label('date'),
    func.count(StepCard.card_id)
    ).filter(
        StepCard.created_at >= start_date,
        StepCard.status == 'help'
    ).group_by('date').all()
    help_counts = {date: count for date, count in help_card_results}

        # --- 3. Chart.js用のデータ形式に整形 ---
    step_data_list = []
    help_data_list = []

    for date_key in date_keys: # 7日間の日付をループ
        step_data_list.append(step_counts.get(date_key, 0)) # その日付の件数、なければ0
        help_data_list.append(help_counts.get(date_key, 0)) # その日付の件数、なければ0

    # Chart.jsに渡す最終的なPython辞書
    chart_data_py = {
        "labels": date_labels, # X軸のラベル
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
    
    # Python辞書をJSON文字列に変換してテンプレートに渡す
    # (JavaScriptで安全に読み込むため)
    chart_data_json = json.dumps(chart_data_py)

    return render_template('personal/PersonalDataErrorCount.html', chart_data=chart_data_json)


# 言語種別比率------------------------------------------------------------------------
@personal_bp.route('/LanguageRatio', methods=['GET', 'POST']) 
def language_ratio_data():
    user_id = current_user.user_id
    user_cards = StepCard.query.filter_by(user_id=user_id).all()

    if not user_cards:
        return jsonify({"labels": [], "values": []})

    tag_names = [tag.tag_name for card in user_cards for tag in card.tags]
    
    if not tag_names:
        return jsonify({"labels": [], "values": []})

    tag_count = Counter(tag_names)

    return jsonify({
        "labels": list(tag_count.keys()),
        "values": list(tag_count.values())
    })

@personal_bp.route('/LanguageRatio', methods=['GET'])
@login_required
def language_ratio_view():
    return render_template('personal/PersonalDataLanguage.html')
    

# エラー種別比率------------------------------------------------------------------------
@personal_bp.route('/ErrorTypes', methods=['GET', 'POST'])
def data_error_type_ratio():
    user_id = current_user.user_id
    user_cards = StepCard.query.filter_by(user_id=user_id).all()

    # カード自体がない場合
    if not user_cards:
        chart_data_json = json.dumps({"labels": [], "datasets": [{"data": [], "backgroundColor": []}]})
        return render_template('personal/PersonalDataErrorTypes.html', chart_data=chart_data_json)

    # エラータイプ（error_type）をカウント
    error_types = [card.error_type for card in user_cards if card.error_type]
    
    # エラータイプが一つもない場合
    if not error_types:
        chart_data_json = json.dumps({"labels": [], "datasets": [{"data": [], "backgroundColor": []}]})
        return render_template('personal/PersonalDataErrorTypes.html', chart_data=chart_data_json)

    error_count = Counter(error_types)

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
    # X軸のラベル 
    date_labels = [(today - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
    # DB検索用の日付
    date_keys = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

    start_date = date_keys[0]  # 7日前の日付

    # --- 2. データベースからコメント数を集計 ---
    # Comment モデルがあると仮定
    from models import Comment  # Comment モデルをインポート
    
    comment_results = db.session.query(
        func.strftime('%Y-%m-%d', Comment.created_at).label('date'),
        func.count(Comment.comment_id)
    ).filter(
        Comment.user_id == user_id,
        Comment.created_at >= start_date
    ).group_by('date').all()
    
    # 高速で検索できるように辞書に変換 (例: {'2025-11-18': 5})
    comment_counts = {date: count for date, count in comment_results}

    # --- 3. Chart.js用のデータ形式に整形 ---
    comment_data_list = []

    for date_key in date_keys:  # 7日間の日付をループ
        comment_data_list.append(comment_counts.get(date_key, 0))  # その日付のコメント件数、なければ0

    # Chart.jsに渡す最終的なPython辞書
    chart_data_py = {
        "labels": date_labels,  # X軸のラベル
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
    
    # Python辞書をJSON文字列に変換してテンプレートに渡す
    chart_data_json = json.dumps(chart_data_py)

    return render_template('personal/PersonalDataComment.html', chart_data=chart_data_json)


# コメント傾向------------------------------------------------------------------------
@personal_bp.route('/Trend', methods=['GET', 'POST'])
def data_comment_trend():
    user_id = current_user.user_id
    
    # --- 1. Comment モデルをインポート ---
    from models import Comment
    
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
