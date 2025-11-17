from flask import Blueprint, render_template, request

share_bp = Blueprint('share', __name__)


# カードライブラリ------------------------------------------------------------------------
@share_bp.route('/share', methods=['GET', 'POST'])
def share_card_library():
    return render_template('share/CardLibrary.html')



# ステップカード共有一覧------------------------------------------------------------------------
@share_bp.route('/share/step_cards', methods=['GET'])
def share_step_card_list():
    """
    タグ検索（GET パラメータ tag を使う実装）。
    実運用では step_cards を DB から取得。
    """
    keyword = request.args.get('tag', '').strip()

    # ここはサンプルデータ（本番では DB から引く）
    step_cards = [
        {'id': 1, 'title': 'C言語基礎', 'tags': ['c言語', 'ポインタ', '入門']},
        {'id': 2, 'title': 'Pythonエラー集', 'tags': ['python', '例外', 'デバッグ']},
        {'id': 3, 'title': 'Flask入門', 'tags': ['python', 'flask', 'web']},
        {'id': 4, 'title': 'C言語メモ', 'tags': ['C言語', 'ビット演算']},
    ]

    matches = []
    if keyword:
        k_lower = keyword.lower()
        for card in step_cards:
            # 各タグを小文字にして部分一致（大文字小文字を無視）
            for t in card['tags']:
                if k_lower in t.lower():
                    matches.append(card)
                    break  # そのカードは既にマッチしているので次のカードへ

    return render_template('share/StepCardShareList.html', keyword=keyword, matches=matches)




# ヘルプカード共有一覧------------------------------------------------------------------------
@share_bp.route('/share/help_cards', methods=['GET', 'POST'])
def share_help_card_list():
    return render_template('share/HelpCardShareList.html')