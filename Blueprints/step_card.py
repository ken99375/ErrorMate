# blueprints/step_card.py
from flask import Blueprint, render_template

step_card_bp = Blueprint("step_card", __name__)

@step_card_bp.route("/list")
def stepcard_list():
    return render_template("ステップカード一覧画面.html")