from flask import Flask

# Flaskアプリのインスタンスを作成
app = Flask(__name__)

# http://127.0.0.1:5000/ にアクセスしたときの処理
@app.route("/")
def hello_world():
    return "Hello, World!"