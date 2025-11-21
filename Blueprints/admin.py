from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/students', methods=['GET'])
@login_required
def view_all_students():
    # 後で実装
    return render_template('admin/students.html')

@admin_bp.route('/cards', methods=['GET'])
@login_required
def view_all_cards():
    # 後で実装
    return render_template('admin/cards.html')

@admin_bp.route('/help-requests', methods=['GET'])
@login_required
def view_all_help_requests():
    # 後で実装
    return render_template('admin/help_requests.html')

@admin_bp.route('/analytics', methods=['GET'])
@login_required
def analytics_dashboard():
    # 後で実装
    return render_template('admin/analytics.html')