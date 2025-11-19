from flask import Blueprint, render_template
from flask import g

main_bp = Blueprint('main', __name__)

@main_bp.before_request
def set_header_theme():
    g.header_theme = "main"

@main_bp.route('/')
def index():
    # templates/index.html をレンダリングして返す
    return render_template('index.html')