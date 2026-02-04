from flask import (
    Blueprint, redirect, url_for, flash, session
)
from flask_login import logout_user

auth_bp = Blueprint('auth', __name__)

# ------------------------------------------------------------
# ログイン（LTI前は使用不可）
# ------------------------------------------------------------
@auth_bp.route('/login')
def login():
    return "Moodle(LTI)から起動してください", 401
    
    
# ------------------------------------------------------------
# ログアウト
# ------------------------------------------------------------
@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('ログアウトしました', 'success')
    return redirect(url_for('main.index'))
