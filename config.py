import os

class Config:

    #app = Flask(__name__)

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'VeryHardToGuessKey'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    #app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

    #db = SQLAlchemy(app)