from flask import Blueprint, render_template, request, redirect, url_for

step_card_bp = Blueprint('step_card', __name__)

@step_card_bp.route('/list')
def list_cards():
    cards = []  # まだDBないならとりあえず空
    return render_template('step_card_list.html', cards=cards)

@step_card_bp.route('/create', methods=['GET', 'POST'])
def create_card():
    if request.method == 'POST':
        # ここでフォームの中身を取る（今は保存はダミーでもOK）
        title = request.form.get('text_title')
        error_code = request.form.get('text_error')
        fix_code = request.form.get('text_fixcode')
        message = request.form.get('text_message')
        result = request.form.get('text_result')

        # TODO: StepCard を作って db に保存する処理を書く

        # 保存後は一覧に戻る
        return redirect(url_for('step_card.create_complete'))

    # GET のときは画面表示だけ
    return render_template('step_card_create.html')


@step_card_bp.route('/create/complete')
def create_complete():
    return render_template('card/StepCardCreateComplate.html')
