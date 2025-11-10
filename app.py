from flask import Flask
from blueprints.main import main_bp

# 他のBlueprintはファイル作成後にコメントアウトを解除する
# from blueprints.auth import auth_bp
# from blueprints.step_card import step_card_bp
# from blueprints.share import share_bp
# from blueprints.admin import admin_bp
# from blueprints.api import api_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key' # 開発用キー

# main_bpのみ登録
app.register_blueprint(main_bp)

# 将来的に有効化する
# app.register_blueprint(auth_bp, url_prefix='/auth')
# app.register_blueprint(step_card_bp, url_prefix='/card')
# app.register_blueprint(share_bp, url_prefix='/library')
# app.register_blueprint(admin_bp, url_prefix='/admin')
# app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)