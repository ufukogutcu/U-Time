from flask import Flask

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from auth.views import auth_blueprint
from diary.views import diary_blueprint
app.register_blueprint(auth_blueprint)
app.register_blueprint(diary_blueprint)

with app.app_context():
    db.drop_all()
    db.create_all()
