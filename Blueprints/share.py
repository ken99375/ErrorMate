from flask import Blueprint, render_template

share_bp = Blueprint('share', __name__)

@share_bp.route('/share', methods=['GET', 'POST'])
def share_card_library():
    return render_template('share/CardLibrary.html')