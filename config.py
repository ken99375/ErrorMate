import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'errormate.db').replace('\\', '/')

class ProductionConfig(Config):
    DEBUG = False
    
    # 【変更点】環境変数を直接読み込みます（なければエラーになるようにします）
    # MySQL (MariaDB) 接続文字列
    # mysqlclientライブラリを使用する標準的な形式
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@{host}/{db_name}".format(
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    db_name=os.environ.get('DB_NAME')
)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}