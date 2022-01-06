import json

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
import requests

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

def get_google_provider_cfg(): 
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@login_manager.user_loader
def load_user(user_id): 
    return User.get(user_id)

@bp.route('/')
def home():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else: 
        return '<a class="button" href="/login">Google Login</a>'

@bp.route('/login')
def login(): 
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@bp.route('/login/callback')
def callback():
    # get authorization code google sent back
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint, 
        authorization_response=request.url, 
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url, 
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    # parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # get user profile information
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else: 
        return "User email not available or not verified by Google.", 400
    
    # create user in db with the information provided by google
    user = User(id_=unique_id, name=users_name, email=users_email, profile_pic=picture)

    if not User.get(unique_id): 
        User.create(unique_id, users_name, users_email, picture)

    # begin user session by logging the user in 
    login_user(user)
    
    return redirect(url_for("auth.home"))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.home"))
