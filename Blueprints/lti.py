# Blueprints/lti.py
from flask import (
    Blueprint, request, redirect,
    url_for, render_template
)
from flask_login import login_user
from pylti.flask import lti
from models import db, User

lti_bp = Blueprint('lti', __name__)

# ---------------------------------------------------
# LTIエラー処理
# ---------------------------------------------------
def lti_error(exception=None):
    print("====== LTI ERROR START ======")
    print(exception)
    print("====== LTI ERROR END ======")

    return render_template(
        'error.html',
        message="LTI認証エラーが発生しました。",
        exception=exception
    ), 500


# ---------------------------------------------------
# LTI Launch（Moodle → ErrorMate）
# ---------------------------------------------------
@lti_bp.route('/launch', methods=['POST'])
@lti(error=lti_error)
def lti_launch(lti):
    """
    MoodleからPOSTされるLTI情報を受け取り、
    ユーザーを作成 or 更新してログインさせる
    """

    # --- LTIから取得できる情報 ---
    moodle_user_id = lti.user_id
    email = lti.lis_person_contact_email_primary
    fullname = lti.lis_person_name_full or "Moodle User"
    roles = (lti.roles or "").lower()
    course_id = lti.context_id

    if not moodle_user_id:
        return "LTI user_id missing", 400

    # --- ロール判定 ---
    if "instructor" in roles or "teacher" in roles:
        role = "teacher"
    elif "learner" in roles or "student" in roles:
        role = "student"
    else:
        role = "guest"

    # --- ユーザー取得 or 作成 ---
    user = User.query.filter_by(
        moodle_user_id=moodle_user_id
    ).first()

    if not user:
        user = User(
            moodle_user_id=moodle_user_id,
            mail=email,
            username=fullname,
            role=role
        )
        db.session.add(user)
    else:
        # Moodle側変更に追従
        user.mail = email
        user.username = fullname
        user.role = role

    db.session.commit()

    # --- セッション固定攻撃対策込みログイン ---
    login_user(user, fresh=True)

    print(
        f"LTI LOGIN SUCCESS: {user.username} "
        f"({user.role}) course={course_id}"
    )

    return redirect(url_for('main.index'))
