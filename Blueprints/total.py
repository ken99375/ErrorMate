from flask import Blueprint, render_template, request, g
from flask_login import login_required, current_user
from models import db, StepCard, User, STATUS_STEP, STATUS_HELP
from sqlalchemy import func
from datetime import datetime, timedelta
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
        active_key="comment_reception_ranking",
        chart_data=chart
    )
    
#  総エラー発生回数
@total_bp.route('/TotalError', methods=['GET'])
@login_required
def total_errors():
    # 先生だけに限定したいなら（任意）
    # if getattr(current_user, "role", None) != "teacher":
    #     abort(403)

    # 何週分出すか（例：直近8週）
    WEEKS = 8

    today = datetime.utcnow().date()
    this_monday = today - timedelta(days=today.weekday())  # 今週の月曜
    week_starts = [this_monday - timedelta(weeks=i) for i in range(WEEKS-1, -1, -1)]
    oldest = week_starts[0]  # 集計開始日

    # ISO週キー（MySQL: %x=ISO年, %v=ISO週）
    week_key_expr = func.date_format(StepCard.created_at, '%x-%v').label('week_key')

    # ステップカード（全生徒）
    step_rows = (
        db.session.query(week_key_expr, func.count(StepCard.card_id))
        .join(User, User.user_id == StepCard.user_id)
        .filter(
            User.role == 'student',
            StepCard.created_at >= oldest,
            StepCard.status == STATUS_STEP
        )
        .group_by('week_key')
        .all()
    )
    step_counts = {wk: cnt for wk, cnt in step_rows}

    # ヘルプカード（全生徒）
    help_rows = (
        db.session.query(week_key_expr, func.count(StepCard.card_id))
        .join(User, User.user_id == StepCard.user_id)
        .filter(
            User.role == 'student',
            StepCard.created_at >= oldest,
            StepCard.status == STATUS_HELP
        )
        .group_by('week_key')
        .all()
    )
    help_counts = {wk: cnt for wk, cnt in help_rows}

    # 画面表示用ラベル（例：02/03〜02/09）
    labels = []
    step_data = []
    help_data = []

    for ws in week_starts:
        we = ws + timedelta(days=6)
        labels.append(f"{ws.strftime('%m/%d')}〜{we.strftime('%m/%d')}")

        iso_year, iso_week, _ = ws.isocalendar()
        key = f"{iso_year:04d}-{iso_week:02d}"  # '%x-%v' と同じ形式に合わせる

        step_data.append(int(step_counts.get(key, 0)))
        help_data.append(int(help_counts.get(key, 0)))

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "ステップカード投稿数",
                "data": step_data,
                "borderColor": "rgb(255, 193, 7)",
                "backgroundColor": "rgba(255, 193, 7, 0.2)",
                "fill": True,
                "tension": 0.15
            },
            {
                "label": "ヘルプカード投稿数",
                "data": help_data,
                "borderColor": "rgb(33, 150, 243)",
                "backgroundColor": "rgba(33, 150, 243, 0.2)",
                "fill": True,
                "tension": 0.15
            }
        ]
    }

    return render_template(
        'total/total_errors.html',
        active_key='total_errors',
        chart_data=json.dumps(chart_data)
    )
    
