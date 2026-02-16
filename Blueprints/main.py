from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    # ロール確認（自動的にテンプレートで処理）
    return render_template('index.html')
    
@main_bp.route("/test/403")
def test_403():
    abort(403)

@main_bp.route("/test/500")
def test_500():
    1 / 0  # わざと例外を起こす（ZeroDivisionError）→ 500

@main_bp.route("/test/501")
def test_501():
    abort(501)