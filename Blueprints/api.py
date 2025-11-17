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
    data = request.json
    title = data.get("title", "")
    message = data.get("message", "")

    text = f"{title}\n{message}"

    if not text.strip():
        return jsonify({"error": "タイトルとメッセージが必要です"}), 400

    prompt = f"""
    以下のテキストから内容を要約し、関連するタグを2つだけ生成してください。
    - 1つ目のタグは、テキスト内容から推測される「プログラミング言語」（例: Python, Java, JavaScript）にしてください。
    - 2つ目のタグは、テキスト内容から推測される「エラーの種類」（例: NameError, TypeError, 文法エラー）にしてください。
    
    出力は ["タグ1","タグ2"] のJSON形式のみで返してください。

    テキスト:
    {text}
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}] # 1回で指示とテキストを両方送る
        }]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)

    # --- ★★★ ここからが不足している可能性のあるコード ★★★ ---

    # APIエラーチェック
    if response.status_code != 200:
        print("★Gemini APIエラー内容 (generate_tags)★")
        print(response.text)
        return jsonify({"error": "Gemini APIエラー"}), 500

    # テキスト抽出
    try:
        result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except KeyError:
        print("★Gemini APIエラー (KeyError)★")
        print(response.text)
        return jsonify({"error": "Gemini APIからの応答形式が不正です"}), 500

    # AIが ```json ... ``` のようなマークダウンを返すことがあるため、それを除去する
    clean_text = result_text.strip()
    if clean_text.startswith('```json'):
        clean_text = clean_text[7:]
    if clean_text.startswith('```'):
        clean_text = clean_text[3:]
    if clean_text.endswith('```'):
        clean_text = clean_text[:-3]
    
    clean_text = clean_text.strip()

    # JSONパース（["タグ1", "タグ2"]形式）
    try:
        tags = json.loads(clean_text)
    except json.JSONDecodeError:
        print("AI 出力 (Raw):", result_text)
        print("AI 出力 (Cleaned):", clean_text)
        return jsonify({"error": "タグ解析に失敗しました"}), 500

    return jsonify({"tags": tags})