from flask import Blueprint, request, jsonify
import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

api_bp = Blueprint('api', __name__)

API_KEY = os.environ.get('GEMINI_API_KEY') or ""

if not API_KEY:
    print("警告：GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")

# エラー解析用モデル
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"


# エラー分析 API
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
        return jsonify({"error": "Gemini APIの解析に失敗しました"}), 500

    return jsonify({"result": ai_text})


# タグ生成 API
@api_bp.route("/generate_tags", methods=["POST"])
def generate_tags():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "テキストが不足しています"}), 400
    
    prompt = f"""
    以下のテキストから内容を要約し、
    関連するタグを2つだけ生成してください。
    出力は ["タグ1","タグ2"] のJSON形式のみで返してください。

    テキスト:
    {text}
    """

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    gemini_url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    response = requests.post(gemini_url, headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({"error": "Gemini APIエラー"}), 500

    result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    try:
        tags = json.loads(result_text)
    except json.JSONDecodeError:
        return jsonify({"error": "タグ解析に失敗しました"}), 500

    return jsonify({"tags": tags})
