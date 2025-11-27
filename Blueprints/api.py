from flask import Blueprint, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_bp = Blueprint('api', __name__)

API_KEY = os.environ.get('GEMINI_API_KEY') or ""

if not API_KEY:
    print("警告：GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")

# -------------------------------------
# Gemini 2.0 Flash（正式版）を使用
# -------------------------------------
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1/models/"
    f"gemini-2.0-flash:generateContent?key={API_KEY}"
)


# ------------------------------------------------
# エラー分析 API
# ------------------------------------------------
@api_bp.route('/analyze-error', methods=['POST'])
def analyze_error():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSONデータがありません。"}), 400

    error_code = data.get('code')
    error_message = data.get('message')

    if not error_code or not error_message:
        return jsonify({"error": "コードまたはメッセージが不足しています。"}), 400

    system_prompt = (
        "あなたはプログラミング学習を支援する優秀なアシスタントです。"
        "以下のエラーコードとエラーメッセージを分析し、以下の3点について日本語で簡潔に回答してください。"
        "1. エラーの根本的な原因は何か。"
        "2. 一般的な修正方法（コード例は不要）。"
        "3. このエラーから学ぶべき重要な概念（1つ）。"
    )

    user_query = f"""
    エラーコード:
    {error_code}

    エラーメッセージ:
    {error_message}
    """

    payload = {
        "contents": [
            {"parts": [{"text": system_prompt}]},
            {"parts": [{"text": user_query}]}
        ]
    }

    response = requests.post(GEMINI_API_URL, json=payload)
    
    try:
        result = response.json()
        ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("★Gemini APIエラー (analyze-error)★")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        print(f"Error: {e}")
        return jsonify({"error": "Gemini APIの解析に失敗しました"}), 500

    return jsonify({"result": ai_text})


# ------------------------------------------------
# タグ生成 API
# ------------------------------------------------
@api_bp.route("/generate_tags", methods=["POST"])
def generate_tags():
    # 1. データ取得（もしJSONでなければ空辞書を使う）
    data = request.get_json() or {}
    
    # 2. JSから送られた3つのデータを取得
    title = data.get("title", "")
    code = data.get("code", "")     # ★追加: コードも受け取る
    message = data.get("message", "")

    # タイトルとメッセージすらない場合はエラー
    if not title and not message:
        return jsonify({"error": "タイトルまたはメッセージが必要です"}), 400

    # 3. プロンプトにコードも含めるように修正
    prompt = f"""
    以下のプログラミングエラーに関する情報から、関連するタグを2つ生成してください。
    - 1つ目のタグは「プログラミング言語」（例: Python, Java, JavaScript）
    - 2つ目のタグは「エラーの種類」（例: NameError, TypeError, SyntaxError）
    
    出力は ["タグ1", "タグ2"] のJSONリスト形式のみで返してください。余計なマークダウンや説明は不要です。

    【エラー情報】
    タイトル: {title}
    コード: {code}
    エラーメッセージ: {message}
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)

        # APIエラーチェック
        if response.status_code != 200:
            print(f"★Gemini API Error: {response.status_code}")
            print(response.text)
            return jsonify({"error": "Gemini APIエラー"}), 500

        # テキスト抽出
        result_json = response.json()
        if "candidates" not in result_json:
            print("★Unexpected Response:", result_json)
            return jsonify({"error": "AIからの応答が空です"}), 500
            
        result_text = result_json["candidates"][0]["content"]["parts"][0]["text"]

        # クリーニング (Markdown除去)
        clean_text = result_text.strip()
        # ```json や ``` を削除
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        
        clean_text = clean_text.strip()

        # JSONパース
        tags = json.loads(clean_text)
        return jsonify({"tags": tags})

    except Exception as e:
        print(f"★Server Error: {e}")
        return jsonify({"error": str(e)}), 500