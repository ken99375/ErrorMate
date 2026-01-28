from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv

api_bp = Blueprint("api", __name__, url_prefix="/api")

load_dotenv()


@api_bp.route("/ai/tags", methods=["POST"])
def generate_tags():
    data = request.get_json(silent=True) or {}

    title = data.get("title", "").lower()
    code = data.get("code", "").lower()
    message = data.get("message", "").lower()

    tags = set()

    text_all = f"{title} {code} {message}"

    # =========================
    # ① Pythonエラー種別
    # =========================
    if "nameerror" in message:
        tags.add("NameError")
    if "typeerror" in message:
        tags.add("TypeError")
    if "attributeerror" in message:
        tags.add("AttributeError")
    if "syntaxerror" in message:
        tags.add("SyntaxError")
    if "keyerror" in message:
        tags.add("KeyError")
    if "indexerror" in message:
        tags.add("IndexError")
    if "importerror" in message or "modulenotfounderror" in message:
        tags.add("ImportError")

    # =========================
    # ② HTTP / API エラー
    # =========================
    if "404" in message:
        tags.add("404")
        tags.add("NotFound")
    if "500" in message:
        tags.add("500")
        tags.add("InternalServerError")
    if "403" in message:
        tags.add("403")
        tags.add("Forbidden")
    if "401" in message:
        tags.add("401")
        tags.add("Unauthorized")
    if "timeout" in message:
        tags.add("Timeout")
    if "too many requests" in message or "429" in message:
        tags.add("RateLimit")

    # =========================
    # ③ フレームワーク・言語
    # =========================
    if "flask" in text_all:
        tags.add("Flask")
    if "django" in text_all:
        tags.add("Django")
    if "fastapi" in text_all:
        tags.add("FastAPI")

    if "python" in text_all or "traceback" in message:
        tags.add("Python")
    if "javascript" in text_all or "js" in title:
        tags.add("JavaScript")
    if "html" in text_all:
        tags.add("HTML")
    if "css" in text_all:
        tags.add("CSS")
    if "json" in text_all:
        tags.add("JSON")

    # =========================
    # ④ DB・データ関連
    # =========================
    if "sql" in text_all:
        tags.add("SQL")
    if "sqlite" in text_all:
        tags.add("SQLite")
    if "mysql" in text_all:
        tags.add("MySQL")
    if "postgres" in text_all:
        tags.add("PostgreSQL")
    if "foreign key" in text_all:
        tags.add("外部キー")
    if "unique constraint" in text_all:
        tags.add("制約違反")

    # =========================
    # ⑤ 認証・セキュリティ
    # =========================
    if "login" in text_all or "auth" in text_all:
        tags.add("認証")
    if "token" in text_all:
        tags.add("トークン")
    if "jwt" in text_all:
        tags.add("JWT")
    if "csrf" in text_all:
        tags.add("CSRF")

    # =========================
    # ⑥ フロントエンド挙動
    # =========================
    if "fetch" in text_all:
        tags.add("fetch")
    if "axios" in text_all:
        tags.add("axios")
    if "cors" in text_all:
        tags.add("CORS")
    if "failed to load resource" in text_all:
        tags.add("通信エラー")

    # =========================
    # ⑦ 日本語トラブル文脈
    # =========================
    if "動かない" in message or "動きません" in message:
        tags.add("不具合")
    if "表示されない" in message:
        tags.add("画面表示")
    if "保存できない" in message or "登録できない" in message:
        tags.add("保存処理")
    if "エラーが出る" in message:
        tags.add("エラー")

    # =========================
    # ⑧ ファイル・構成
    # =========================
    if ".py" in text_all:
        tags.add("Pythonファイル")
    if ".js" in text_all:
        tags.add("JSファイル")
    if ".html" in text_all:
        tags.add("HTMLファイル")

    # =========================
    # ⑨ フォールバック
    # =========================
    if not tags:
        tags.add("技術相談")
        tags.add("未分類")

    # 最大7個まで
    result = list(tags)[:7]

    return jsonify({"tags": result})
