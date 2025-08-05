import os


class Config:
    SECRET_KEY = '767f67d340f46cf1b5c22434ccfeba31'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mynotes.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    UPLOAD_CATEGORY = os.path.join('app', 'static', 'category')
    UPLOAD_PROFILE = os.path.join('app', 'static', 'profile')
