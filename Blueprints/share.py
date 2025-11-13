from flask import Blueprint, render_template

share_bp = Blueprint('share', __name__)


# カードライブラリ------------------------------------------------------------------------
@share_bp.route('/share', methods=['GET', 'POST'])
def share_card_library():
    return render_template('share/CardLibrary.html')


# ステップカード共有一覧------------------------------------------------------------------------
@share_bp.route('/share/step_cards', methods=['GET', 'POST'])
def share_step_card_list():
    return render_template('share/StepCardShareList.html')


# ヘルプカード共有一覧------------------------------------------------------------------------
@share_bp.route('/share/help_cards', methods=['GET', 'POST'])
def share_help_card_list():
    return render_template('share/HelpCardShareList.html')