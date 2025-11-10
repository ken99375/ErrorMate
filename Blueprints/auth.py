from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth')
def index():
    # templates/login.html をレンダリングして返す
    return render_template('login.html')