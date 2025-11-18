import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    # ローカル開発用: SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'errormate.db').replace('\\', '/')

class ProductionConfig(Config):
    DEBUG = False
    
    # AWSの環境変数を取得
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME')

    # AWS上にいるかどうかの判定（DB_HOSTがあるかどうか）
    if host:
        # AWS用: MariaDB (MySQL) に接続
        SQLALCHEMY_DATABASE_URI = f'mysql://{user}:{password}@{host}/{db_name}'
    else:
        # 万が一変数が取れない場合のフォールバック（またはローカルテスト用）
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'errormate.db').replace('\\', '/')

# 設定の割り当て
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    
    # ★ここ重要：AWSはデフォルト設定を読み込むことが多いので、
    # 本番(ProductionConfig)をデフォルトにしておきます。
    # ローカルで動かすときは必要に応じて自動でSQLiteに落ちるようになっています。
    'default': ProductionConfig
}