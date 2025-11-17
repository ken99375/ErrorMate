from flask import Blueprint, render_template, request

share_bp = Blueprint('share', __name__)


# カードライブラリ------------------------------------------------------------
@share_bp.route('/share', methods=['GET', 'POST'])
def share_card_library():
    return render_template('share/CardLibrary.html')


# ステップカード共有一覧------------------------------------------------------
@share_bp.route('/share/step_cards', methods=['GET'])
def share_step_card_list():
    """
    タグ検索（GET パラメータ tag を使う実装）
    実運用では step_cards を DB から取得。
    """
    keyword = request.args.get('tag', '').strip()

    # サンプルデータ（将来 DB から読み込む）
    step_cards = [
        {'id': 1, 'title': 'C言語基礎', 'tags': ['c言語', 'ポインタ', '入門']},
        {'id': 2, 'title': 'Pythonエラー集', 'tags': ['python', '例外', 'デバッグ']},
        {'id': 3, 'title': 'Flask入門', 'tags': ['python', 'flask', 'web']},
        {'id': 4, 'title': 'C言語メモ', 'tags': ['c言語', 'ビット演算']},
    ]

    matches = []
    if keyword:
        k_lower = keyword.lower()
        for card in step_cards:
            for t in card['tags']:
                if k_lower in t.lower():
                    matches.append(card)
                    break  

    return render_template('share/StepCardShareList.html',keyword=keyword,matches=matches)


# ヘルプカード共有一覧--------------------------------------------------------
@share_bp.route('/share/help_cards', methods=['GET'])
def share_help_card_list():
    keyword = request.args.get('tag', '').strip()

    # サンプルデータ（将来 DB から読み込む）
    help_cards = [
        {'id': 101, 'title': 'Python 入門', 'tags': ['python', '基礎', 'コード']},
        {'id': 102, 'title': 'Git の使い方', 'tags': ['git', 'バージョン管理', 'push']},
        {'id': 103, 'title': 'VSCode トラブルシュート', 'tags': ['vscode', '設定', 'プラグイン']},
        {'id': 104, 'title': 'Windows ショートカット', 'tags': ['windows', 'ショートカット']},
        {'id': 105, 'title': 'Windows 裏技', 'tags': ['windows', '裏技']},
    ]

    matches = []
    if keyword:
        k_lower = keyword.lower()
        for card in help_cards:
            for t in card['tags']:
                if k_lower in t.lower():
                    matches.append(card)
                    break

    return render_template('share/HelpCardShareList.html',keyword=keyword,matches=matches)
