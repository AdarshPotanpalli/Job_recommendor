from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendor.db' # SQLite3 database uri
app.config['SECRET_KEY'] = '425fd48fc3df3b040a4e6b91' #12 bytes secret key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16 MB
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
db = SQLAlchemy(app) # creating an instance of database
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page' #page to redirect to access fields requiring login
login_manager.login_message_category = 'info' # flash message category for login required

from recommendor import routes

