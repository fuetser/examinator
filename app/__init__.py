from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SECRET_KEY"] = "Wh-6aiKd29eC4-6cCffTRKTciCA"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from app import errors, models, routes


# with app.app_context():
#     db.create_all()
