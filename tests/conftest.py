import os
import sys
import uuid
from uuid import uuid4

import requests
from flask.ext.loopback import FlaskLoopback
from urlobject import URLObject as URL

import pytest
from backslash import Backslash as BackslashClient
from flask_app import app, models

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def pytest_addoption(parser):
    parser.addoption("--url", action="store", default=None)


@pytest.fixture
def client(webapp_without_login, runtoken):
    return BackslashClient('http://{0}'.format(webapp_without_login.hostname), runtoken=runtoken)

@pytest.fixture
def backslash_url(request):
    url = request.config.getoption("--url")
    if url is None:
        pytest.skip()
    return URL(url)

@pytest.fixture
def webapp(testuser, request):
    returned = _create_webapp(request)
    returned.post('/testing_login')
    return returned

@pytest.fixture
def webapp_without_login(request):
    return _create_webapp(request)

def _create_webapp(request):
    returned = Webapp(app.create_app({
        'SQLALCHEMY_DATABASE_URI': 'postgresql://127.0.0.1/backslash-ut',
        'SECRET_KEY': 'testing-key',
        'TESTING': True,
        'SECURITY_PASSWORD_SALT': 'testing_salt',
    }))
    returned.activate()
    request.addfinalizer(returned.deactivate)
    returned.app.extensions['security'].password_salt = returned.app.config['SECURITY_PASSWORD_SALT']
    return returned

@pytest.fixture(scope='function', autouse=True)
def db(request, webapp_without_login):
    with webapp_without_login.app.app_context():
        models.db.session.close()
        models.db.drop_all()
        models.db.create_all()
    return models.db

@pytest.fixture
def runtoken(db, webapp_without_login, testuser):
    with webapp_without_login.app.app_context():
        token_string = str(uuid4())
        token = models.RunToken(user=testuser, token=token_string)
        db.session.add(token)
        db.session.commit()
    return token_string

@pytest.fixture
def testuser(db, webapp_without_login, testuser_email):
    with webapp_without_login.app.app_context():
        user = models.User(email=testuser_email, active=True)
        db.session.add(user)
        db.session.commit()
    return user

@pytest.fixture
def testuser_email():
    return 'testing@localhost'


class Webapp(object):

    def __init__(self, app):
        super(Webapp, self).__init__()
        self.app = app
        self.loopback = FlaskLoopback(self.app)
        self.hostname = str(uuid.uuid1())

    def activate(self):
        self.loopback.activate_address((self.hostname, 80))

    def deactivate(self):
        self.loopback.deactivate_address((self.hostname, 80))

    def _request(self, method, path, *args, **kwargs):
        raw_response = kwargs.pop("raw_response", False)
        if path.startswith("/"):
            path = path[1:]
            assert not path.startswith("/")
        returned = requests.request(method, "http://{0}/{1}".format(self.hostname, path), *args, **kwargs)
        if raw_response:
            return returned

        returned.raise_for_status()
        return returned.json()

def _make_request_shortcut(method_name):
    def json_method(self, *args, **kwargs):
        return self._request(method_name, *args, **kwargs)

    json_method.__name__ = method_name
    setattr(Webapp, method_name, json_method)

    def raw_method(self, *args, **kwargs):
        return self._request(method_name, raw_response=True, *args, **kwargs)

    raw_method.__name__ = "{0}_raw".format(method_name)
    setattr(Webapp, raw_method.__name__, raw_method)

for _method in ("get", "put", "post", "delete"):
    _make_request_shortcut(_method)
