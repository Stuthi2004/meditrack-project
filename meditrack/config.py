import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'meditrack_secret')

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_DIR = os.path.join(BASE_DIR, 'database')
    os.makedirs(DATABASE_DIR, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(DATABASE_DIR, 'meditrack.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
