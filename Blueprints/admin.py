from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import Blueprint, render_template, jsonify, g
from flask_login import login_required, current_user
from models import db, StepCard, Comment, Tag
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from collections import Counter

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/share', methods=['GET'])
def share_card_library():
    # --- 1. 過去7日間の日付ラベルを生成 ---
    today = datetime.utcnow().date()
    # X軸のラベル (例: 11/25)
    date_labels = [(today - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
    # DB検索用の日付キー (例: 2025-11-25)
    date_keys = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

    start_date = date_keys[0] # 7日前の日付

    # --- 2. データベースからデータを集計 (全生徒対象) ---
    
    # (A) 全生徒のステップカード (status='public') の日別カウント
    # ★修正点: .filter(StepCard.user_id == user_id) を削除しました
    step_card_results = db.session.query(
        func.date_format(StepCard.created_at, '%Y-%m-%d').label('date'),
        func.count(StepCard.card_id)
    ).filter(
        StepCard.created_at >= start_date,
        StepCard.status == 'public'
    ).group_by('date').all()
    
    # 日付ごとの辞書に変換
    step_counts = {date: count for date, count in step_card_results}

    # (B) 全生徒のヘルプカード (status='help') の日別カウント
    # ★修正点: こちらも user_id のフィルタを削除
    help_card_results = db.session.query(
        func.date_format(StepCard.created_at, '%Y-%m-%d').label('date'),
        func.count(StepCard.card_id)
    ).filter(
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
                "label": '全生徒のステップカード数',  # ラベルを変更
                "data": step_data_list,
                "borderColor": 'rgb(255, 205, 86)',
                "backgroundColor": 'rgba(255, 205, 86, 0.2)',
                "fill": True,
                "tension": 0.01
            },
            {
                "label": '全生徒のヘルプカード数',    # ラベルを変更
                "data": help_data_list,
                "borderColor": 'rgb(54, 162, 235)',
                "backgroundColor": 'rgba(54, 162, 235, 0.2)',
                "fill": True,
                "tension": 0.01
            }
        ]
    }
    
    chart_data_json = json.dumps(chart_data_py)
    
    # ★重要: テンプレートに chart_data を渡す記述を追加しました
    return render_template('share/CardLibrary.html', chart_data=chart_data_json)

@admin_bp.route('/TotalErrorCount', methods=['GET'])
@login_required
def view_all_help_requests():
    return render_template('Total/TotalDateErrorCount.html')

