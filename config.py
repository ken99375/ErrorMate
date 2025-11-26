import os
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'dev'      # 適当でいいけど本番は変える
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    
    # --- ここを修正しました ---
    # .env からデータベース接続情報を取得する
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME')

    # もし .env の情報が揃っていれば RDS (MySQL) を使う
    if user and host:
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{user}:{password}@{host}/{db_name}'
    else:
        # 情報がなければ SQLite (ローカル) を使う（バックアップ用）
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
            basedir, 'instance', 'errormate.db'
        ).replace('\\', '/')

class ProductionConfig(Config):
    DEBUG = False
    # 本番用の設定を書く

# config 辞書
config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}