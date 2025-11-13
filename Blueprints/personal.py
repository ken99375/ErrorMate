from flask import Blueprint, render_template

personal_bp = Blueprint('personal', __name__)


# エラー発生回数------------------------------------------------------------------------
@personal_bp.route('/ErrorCount', methods=['GET', 'POST'])
def data_error_count():
    return render_template('personal/PersonalDataErrorCount.html')


# 言語種別比率------------------------------------------------------------------------
@personal_bp.route('/LanguageRatio', methods=['GET', 'POST'])
def data_language_ratio():
    return render_template('personal/PersonalDataLanguage.html')


# エラー種別比率------------------------------------------------------------------------
@personal_bp.route('/ErrorTypes', methods=['GET', 'POST'])
def data_error_type_ratio():
    return render_template('personal/PersonalDataErrorTypes.html')

# コメント回数------------------------------------------------------------------------
@personal_bp.route('/Comment', methods=['GET', 'POST'])
def data_comment_count():
    return render_template('personal/PersonalDataComment.html')


# コメント傾向------------------------------------------------------------------------
@personal_bp.route('/Trend', methods=['GET', 'POST'])
def data_comment_trend():
    return render_template('personal/PersonalDataTrend.html')