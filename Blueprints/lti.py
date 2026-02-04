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
def lti_launch():
    # まずはここに到達するか確認
    print("LTI RAW LAUNCH (Blueprint)")
    print(request.form)
    return redirect(url_for('main.index'))

