
import logbook
import requests
from flask import (abort, Blueprint, current_app, jsonify, request,
                   session)
from flask.ext.security import SQLAlchemyUserDatastore
from itsdangerous import BadSignature, TimedSerializer

from flask_security.utils import login_user, verify_and_update_password

from .models import db, Role, User
from .utils.oauth2 import get_oauth2_identity

_logger = logbook.Logger(__name__)

_MAX_TOKEN_AGE = 60 * 60 * 24 * 7  # one week

auth = Blueprint("auth", __name__, template_folder="templates")

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


@auth.route('/testing_login', methods=['POST'])
def testing_login():
    if not current_app.config.get('TESTING'):
        abort(requests.codes.not_found)

    user_id = request.args.get('user_id')
    if user_id is not None:
        user = User.query.get_or_404(int(user_id))
    else:
        testing_email = 'testing@localhost'
        user = _get_or_create_user({'email': testing_email})
    assert user
    login_user(user)
    user_info = {}
    return _make_success_login_response(user, user_info)

@auth.route("/login", methods=['POST'])
def login():

    auth_code = (request.json or {}).get('authorizationCode')
    if auth_code is None:
        abort(requests.codes.unauthorized)

    user_info = get_oauth2_identity(auth_code)
    if not user_info:
        abort(requests.codes.unauthorized)

    _check_alowed_email_domain(user_info)

    user = _get_or_create_user(user_info)
    _fix_first_user_role(user)

    login_user(user)

    return _make_success_login_response(user, user_info)

def _make_success_login_response(user, user_info):
    token = _generate_token(user, user_info)
    _logger.debug('OAuth2 login success for {}. Token: {!r}', user_info, token)

    return jsonify({
        'auth_token': token,
        'user_info': user_info,
    })


@auth.route("/reauth", methods=['POST'])
def reauth():
    token = (request.json or {}).get('auth_token')
    if token is None:
        abort(requests.codes.unauthorized)
    try:
        token_data = _get_token_serializer().loads(
            token, max_age=_MAX_TOKEN_AGE)
    except BadSignature:
        abort(requests.codes.unauthorized)
    user = User.query.get_or_404(token_data['user_id'])

    login_user(user)

    return jsonify({
        'auth_token': token,
        'user_info': token_data['user_info'],
    })


def _generate_token(user, user_info):
    return _get_token_serializer().dumps({
        'user_id': user.id,
        'user_info': user_info})


def _get_token_serializer():
    return TimedSerializer(current_app.config['SECRET_KEY'])


def _get_or_create_user(user_info):
    email = user_info['email']
    user = user_datastore.get_user(email)
    if not user:
        user = user_datastore.create_user(
            active=True,
            email=email)
        user_datastore.db.session.commit()

    user_info['user_id'] = user.id
    user_info['roles'] = [role.name for role in user.roles]
    user_info['can'] = {role.name: True for role in user.roles}

    _logger.debug('User info: {}', user_info)

    return user


def _fix_first_user_role(user):
    if User.query.count() == 1:
        user_datastore.add_role_to_user(user, 'admin')
        user_datastore.db.session.commit()


def _check_alowed_email_domain(user_info):
    email = user_info['email']
    domain = email.split('@', 1)
    allowed = current_app.config.get('ALLOWED_EMAIL_DOMAINS')
    if allowed is None:
        return
    if domain not in allowed:
        _logger.error('User {} has a disallowed email domain!', email)
        abort(requests.codes.unauthorized)

