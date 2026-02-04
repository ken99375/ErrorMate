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
# @lti(current_app, error=lti_error)
def lti_launch(lti):
    print("LTI LAUNCH VERIFIED")

    moodle_user_id = lti.user_id
    email = lti.lis_person_contact_email_primary
    fullname = lti.lis_person_name_full or "Moodle User"
    roles = (lti.roles or "").lower()

    # ロール判定
    if "instructor" in roles or "teacher" in roles:
        role = "teacher"
    else:
        role = "student"

    # ユーザー取得 or 作成
    user = User.query.filter_by(moodle_user_id=moodle_user_id).first()
    if not user:
        user = User(
            moodle_user_id=moodle_user_id,
            mail=email,
            username=fullname,
            role=role
        )
        db.session.add(user)
        db.session.commit()

    # ★これが今まで無かった
    login_user(user, fresh=True)

    print("LOGIN SUCCESS:", user.username)
    return redirect(url_for('main.index'))

