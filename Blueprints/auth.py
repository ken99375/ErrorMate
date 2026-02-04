from flask import (
    Blueprint, redirect, url_for, flash, session
)

auth_bp = Blueprint('auth', __name__)

# ------------------------------------------------------------
# ログイン（LTI前は使用不可）
# ------------------------------------------------------------
@auth_bp.route('/login')
def login():
    flash('現在はMoodle連携のみ利用可能です', 'error')
    return redirect(url_for('index'))


# ------------------------------------------------------------
# ログアウト
# ------------------------------------------------------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('ログアウトしました', 'success')
    return redirect(url_for('main.index'))
