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

# エラー解析用モデル（v1beta → v1 に書き換え）
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
    result = response.json()

    try:
        ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        print(result)
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
    以下のテキストから内容を要約し、
    関連するタグを2つだけ生成してください。
    出力は ["タグ1","タグ2"] のJSON形式のみで返してください。

    テキスト:
    {text}
    """

    # 統一して 2.0 Flash を使用
    gemini_url = (
        f"https://generativelanguage.googleapis.com/v1/models/"
        f"gemini-2.0-flash:generateContent?key={API_KEY}"
    )

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(gemini_url, headers=headers, json=payload)

    # APIエラーチェック
    if response.status_code != 200:
        print("★Gemini APIエラー内容★")
        print(response.text)
        return jsonify({"error": "Gemini APIエラー"}), 500

    # テキスト抽出
    result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    # JSONパース（["タグ1", "タグ2"]形式）
    try:
        tags = json.loads(result_text)
    except json.JSONDecodeError:
        print("AI 出力:", result_text)
        return jsonify({"error": "タグ解析に失敗しました"}), 500

    return jsonify({"tags": tags})
