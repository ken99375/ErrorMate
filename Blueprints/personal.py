from flask import Blueprint, render_template

personal_bp = Blueprint('personal', __name__)

@personal_bp.route('/ErrorCount', methods=['GET', 'POST'])
def data_error_count():
    return render_template('personal/PersonalDataErrorCount.html')