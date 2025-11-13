from flask import Blueprint, render_template, request, redirect, url_for

help_bp = Blueprint('help', __name__)

@help_bp.route('/create', methods=['GET', 'POST'])
def create_help_card():
        # if request.method == 'POST':
        # # フォーム値取得（保存処理をここに追加）
        # title = request.form.get('title')
        # code = request.form.get('code')
        # message = request.form.get('message')
        # tags = request.form.get('tags')
        # # TODO: DB 保存など
        # return redirect(url_for('help.post_complete'))
    return render_template('help/help_card_create.html')