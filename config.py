class Config:
    SECRET_KEY = 'dev'      # 適当でいいけど本番は変える
    DEBUG = False

# class DevelopmentConfig(Config):
#     DEBUG = True
#     # DB とかあればここに書く
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///errormate.db'  # ここ追加
#     SQLALCHEMY_TRACK_MODIFICATIONS = False              # おまけでOFFにしとく

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        basedir, 'instance', 'errormate.db'
    ).replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    # 本番用の設定を書く

# ← これがないから ImportError になってる
config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}