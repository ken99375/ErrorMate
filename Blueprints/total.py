from flask import Blueprint, render_template

total_bp = Blueprint('total', __name__)

@total_bp.route('/total', methods=['GET', 'POST'])
def total_data_error_():
    return render_template('index.html')