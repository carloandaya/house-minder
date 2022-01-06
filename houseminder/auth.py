from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from oauthlib.oauth2 import WebApplicationClient

from houseminder.user import User

bp = Blueprint('auth', __name__)

GOOGLE_CLIENT_ID = current_app.config['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET = current_app.config['GOOGLE_CLIENT_SECRET']
GOOGLE_DISCOVERY_URL = current_app.config['GOOGLE_DISCOVERY_URL']

# flask-login setup
login_manager = LoginManager()
login_manager.init_app(current_app)

# oauth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id): 
    return User.get(user_id)

@bp.route('/')
def home(): 
    return 'Hello, world!'

@bp.route('/login')
def login(): 
    return 'Hello, login page!'

@bp.route('/login/callback')
def callback(): 
    return 'Hello, callback!'
