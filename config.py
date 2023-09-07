# config.py
class Config:
    PASSWORD_HASH = 'root'
    SESSION_TYPE = 'filesystem'
    ALLOW_OLD_SESSIONS = True # Wether to accept old sessions or not

    SQLALCHEMY_DATABASE_URI = "sqlite:///databases/test.db"

    DEBUG=True
    HOST='127.0.0.1'
    PORT=5000


