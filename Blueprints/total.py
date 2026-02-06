from flask import Blueprint, render_template, request, g
from flask_login import login_required, current_user
from sqlalchemy import func
import json

from extensions import db
from models import User, StepCard, Comment

total_bp = Blueprint("total", __name__, url_prefix="/total")


@total_bp.before_request
def set_header_color():
    # 必要なら色クラスを変えてOK
    g.header_class = "header-analysis"


# ステップカード投稿数
@total_bp.route('/StepcardRanking', methods=['GET', 'POST'])
@login_required
def stepcard_post_ranking():
    # 生徒一覧
    students = db.session.query(User.user_id, User.user_name).filter(
        User.role == "student"
    ).all()

    # 生徒が0なら空グラフ
    if not students:
        chart = {"labels": [], "datasets": [{"label": "ステップカード投稿数", "data": []}]}
        return render_template(
            "total/stepcard_post_ranking.html",
            active_key="stepcard_post_ranking",
            chart_data=json.dumps(chart)
        )

    # ステップカード数（status='step'）を user_id ごとに集計
    rows = db.session.query(
        StepCard.user_id,
        func.count(StepCard.card_id).label("cnt")
    ).filter(
        StepCard.status == "step"
    ).group_by(StepCard.user_id).all()

    counts = {uid: int(cnt) for uid, cnt in rows}

    # 多い順に並べ替え
    ranking = []
    for uid, name in students:
        display = name if name else f"user{uid}"
        label = f"{display}さん" if (display and not str(display).endswith("さん")) else str(display)
        ranking.append({"name": label, "count": counts.get(uid, 0)})
    ranking.sort(key=lambda x: x["count"], reverse=True)

    chart = {
        "labels": [r["name"] for r in ranking],
        "datasets": [{
            "label": "ステップカード投稿数",
            "data": [r["count"] for r in ranking],
        }]
    }

    return render_template(
        "total/stepcard_post_ranking.html",
        active_key="stepcard_post_ranking",
        chart_data=chart
    )

#  コメント送信数
@total_bp.route('/CommentPost', methods=['GET', 'POST'])
@login_required
def comment_post_ranking():
    # 生徒一覧
    students = db.session.query(User.user_id, User.user_name).filter(
        User.role == "student"
    ).all()

    # 生徒が0なら空グラフ
    if not students:
        chart = {"labels": [], "datasets": [{"label": "コメント送信数", "data": []}]}
        return render_template(
            "total/comment_post_ranking.html",
            active_key="comment_post_ranking",
            chart_data=chart
        )

    # コメント数を user_id ごとに集計
    rows = db.session.query(
        Comment.user_id,
        func.count(Comment.comment_id).label("cnt")
    ).join(User, User.user_id == Comment.user_id).filter(
        User.role == "student"
    ).group_by(Comment.user_id).all()

    counts = {uid: int(cnt) for uid, cnt in rows}

    # 多い順に並べ替え
    ranking = []
    for uid, name in students:
        display = name if name else f"user{uid}"
        label = f"{display}さん" if (display and not str(display).endswith("さん")) else str(display)
        ranking.append({"name": label, "count": counts.get(uid, 0)})
    ranking.sort(key=lambda x: x["count"], reverse=True)

    chart = {
        "labels": [r["name"] for r in ranking],
        "datasets": [{
            "label": "コメント送信数",
            "data": [r["count"] for r in ranking]
        }]
    }

    return render_template(
        "total/comment_post_ranking.html",
        active_key="comment_post_ranking",
        chart_data=chart
    )
    
#  コメント受信数
@total_bp.route('/CommentReceive', methods=['GET', 'POST'])
@login_required
def comment_reception_ranking():
    # 生徒一覧
    students = db.session.query(User.user_id, User.user_name).filter(
        User.role == "student"
    ).all()

    # 生徒が0なら空グラフ
    if not students:
        chart = {"labels": [], "datasets": [{"label": "コメント受信数", "data": []}]}
        return render_template(
            "total/comment_receive_ranking.html",
            active_key="comment_receive_ranking",
            chart_data=chart
        )

    # コメント受信数を集計：
    # StepCard.user_id（カード投稿者＝受信者）ごとに、カードに付いたコメント数を数える
    # 自分が自分のカードに書いたコメントは除外（受信っぽくないので）
    rows = (
        db.session.query(
            StepCard.user_id.label("receiver_id"),
            func.count(Comment.comment_id).label("cnt")
        )
        .join(Comment, Comment.card_id == StepCard.card_id)
        .join(User, User.user_id == StepCard.user_id)
        .filter(
            User.role == "student",
            StepCard.status == "step",
            Comment.user_id != StepCard.user_id  # ←自作自演を含めたいならこの行を消す
        )
        .group_by(StepCard.user_id)
        .all()
    )

    counts = {uid: int(cnt) for uid, cnt in rows}

    # 多い順に並べ替え
    ranking = []
    for uid, name in students:
        display = name if name else f"user{uid}"
        label = f"{display}さん" if (display and not str(display).endswith("さん")) else str(display)
        ranking.append({"name": label, "count": counts.get(uid, 0)})

    ranking.sort(key=lambda x: x["count"], reverse=True)

    chart = {
        "labels": [r["name"] for r in ranking],
        "datasets": [{
            "label": "コメント受信数",
            "data": [r["count"] for r in ranking]
        }]
    }

    return render_template(
        "total/comment_reception_ranking.html",
        active_key="comment_reception_ranking   ",
        chart_data=chart
    )
    
#  総エラー発生回数
@total_bp.route('/TotalError', methods=['GET', 'POST'])
@login_required
def total_errors():
    return render_template('total/total_errors.html', active_key='total_errors')
    
