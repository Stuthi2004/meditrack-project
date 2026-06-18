import os

class Config:
    SECRET_KEY = "meditrack_secret"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR, "database", "meditrack.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False