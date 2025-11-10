from flask import Blueprint, render_template, request, redirect, url_for



# 名前が step_card → url_for('step_card.○○') で呼び出す時の前半部分になる。
step_card_bp = Blueprint('step_card', __name__)



#ーーーーーーーーーーーーー一覧画面ーーーーーーーーーーーーーーーーーー#
# /card/list にアクセスした時に動く。
@step_card_bp.route('/list')
def list_cards():
    # 本来ここに DB から取ってきたカード一覧を入れる想定。
    cards = []  # まだDBないならとりあえず空
    # テンプレ側では cards を受け取って、「0件なら真ん中の新規作成だけ表示」みたいな if 分岐に使ってる。
    return render_template('step_card_list.html', cards=cards)

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー#


#ーーーーーーーーーー新規作成画面 ー 保存処理ーーーーーーーーーーーーー#
# GET と POST の2種類のリクエストを受け付ける。
# GET のとき：画面表示
# POST のとき：フォーム送信（保存）
@step_card_bp.route('/create', methods=['GET', 'POST'])
def create_card():
    # 保存ボタンを押した後の処理はこちら側に入る。
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

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー#


#ーーーーーーーーーーーーーーー保存完了画面ーーーーーーーーーーーーーー#

# /card/create/complete にアクセスした時の処理。
# templates フォルダの中に card サブフォルダがあって、
# その中の StepCardCreateComplate.html を取ってくる想定。
@step_card_bp.route('/create/complete')
def create_complete():
    return render_template('card/StepCardCreateComplate.html')

#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー#
