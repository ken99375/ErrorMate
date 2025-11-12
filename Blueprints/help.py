from flask import Blueprint, render_template

help_bp = Blueprint('help', __name__)

@help_bp.route('/create', methods=['GET', 'POST'])
def create_help_card():
    return render_template('help/help_card_create.html')