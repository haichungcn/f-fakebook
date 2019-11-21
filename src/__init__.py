import os
from flask import Blueprint, Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, logout_user, login_user, current_user, login_required
from flask_migrate import Migrate

app = Flask(__name__, static_folder="../static")
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# setup flask migration
migrate = Migrate(app, db)

# setup Flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "root.login" #redirect to login function if user not logged in

# Models:
from src.models import User

## Setup login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

## Controllers:
from src.components.root import root_blueprint
app.register_blueprint(root_blueprint, url_prefix='/')

from src.components.post import post_blueprint
app.register_blueprint(post_blueprint, url_prefix='/post')

from src.components.user import user_blueprint
app.register_blueprint(user_blueprint, url_prefix='/user')
