# config.py

class Config:
    SECRET_KEY = 'dev'      # 適当でいいけど本番は変える
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    # DB とかあればここに書く
    # SQLALCHEMY_DATABASE_URI = "..."

class ProductionConfig(Config):
    DEBUG = False
    # 本番用の設定を書く

# ← これがないから ImportError になってる
config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
