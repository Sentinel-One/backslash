import operator

import requests

from flask import Blueprint, abort, request, session
from flask.ext.security.core import current_user
from flask_restful import Api, reqparse
from sqlalchemy import text

from ..models import Comment, Error, Session, Test, User
from ..utils.rest import ModelResource
from ..utils import statuses

blueprint = Blueprint('rest', __name__, url_prefix='/rest')


rest = Api(blueprint)


def _resource(*args, **kwargs):
    def decorator(resource):
        rest.add_resource(resource, *args, **kwargs)
        return resource
    return decorator

##########################################################################

@_resource('/sessions', '/sessions/<int:object_id>')
class SessionResource(ModelResource):

    MODEL = Session
    DEFAULT_SORT = (Session.start_time.desc(),)
    from .filter_configs import SESSION_FILTERS as FILTER_CONFIG

    def _get_iterator(self):
        returned = super(SessionResource, self)._get_iterator()
        if request.args.get('show_archived') != 'true':
            returned = returned.filter(Session.archived == False)
        return returned

@_resource('/tests', '/tests/<int:object_id>', '/sessions/<int:session_id>/tests')
class TestResource(ModelResource):

    MODEL = Test
    DEFAULT_SORT = (Test.start_time.desc(),)
    from .filter_configs import TEST_FILTERS as FILTER_CONFIG

    def _get_iterator(self):
        session_id = request.args.get('session_id')
        if session_id is None:
            session_id = request.view_args.get('session_id')
        if session_id is not None:
            return Test.query.filter(Test.session_id == session_id).order_by(*self.DEFAULT_SORT)
        return super(TestResource, self)._get_iterator()


session_test_query_parser = reqparse.RequestParser()
session_test_query_parser.add_argument('session_id', type=int, default=None)
session_test_query_parser.add_argument('test_id', type=int, default=None)

@_resource('/errors')
class ErrorResource(ModelResource):

    MODEL = Error

    def _get_iterator(self):
        args = session_test_query_parser.parse_args()
        if args.session_id is not None:
            return Error.query.join((Session, Error.session)).filter(Session.id == args.session_id)
        elif args.test_id is not None:
            return Error.query.join((Test, Error.test)).filter(Test.id == args.test_id)
        abort(requests.codes.bad_request)


@_resource('/users', '/users/<int:object_id>')
class UserResource(ModelResource):

    ONLY_FIELDS = ['id', 'email']
    MODEL = User

    def _get_iterator(self):
        abort(requests.codes.unauthorized)

    def _get_object_by_id(self, object_id):
        user = current_user
        if not user.is_authenticated() or user.id != object_id:
            abort(requests.codes.unauthorized)
        return User.query.get_or_404(int(object_id))




@_resource('/comments', '/comments/<int:object_id>')
class CommentsResource(ModelResource):

    MODEL = Comment
    DEFAULT_SORT = (Comment.timestamp.asc(),)

    def _get_iterator(self):
        args = session_test_query_parser.parse_args()
        if args.session_id is not None:
            returned = Comment.query.join((Session, Comment.session)).filter(Session.id == args.session_id)
        elif args.test_id is not None:
            returned = Comment.query.join((Test, Comment.test)).filter(Test.id == args.test_id)
        else:
            abort(requests.codes.bad_request)
        return returned.join(User)
