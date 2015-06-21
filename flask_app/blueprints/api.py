import datetime

import requests
from flask import abort, Blueprint, request
from flask.ext.simple_api import SimpleAPI
from flask.ext.security import current_user

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from ..models import db, Error, Session, SessionMetadata, Test, TestMetadata
from ..utils import get_current_time
from ..utils.api_utils import API_SUCCESS, auto_commit, auto_render, requires_login_or_runtoken

blueprint = Blueprint('api', __name__, url_prefix='/api')

api = SimpleAPI(blueprint)

def API(func):
    return api.include(requires_login_or_runtoken(auto_render(auto_commit(func))))

##########################################################################

@API
def set_product(id: int,
                name: str=None,
                version: str=None,
                revision: str=None):
    update = {'product_name': name, 'product_version': version, 'product_revision': revision}
    if not Session.query.filter(Session.id == id).update(update):
        abort(requests.codes.not_found)


@API
def report_session_start(logical_id: str=None,
                         hostname: str=None,
                         product_name: str=None,
                         product_version: str=None,
                         product_revision: str=None,
                         total_num_tests: int=None,
                         metadata: dict=None,
                     ):
    if hostname is None:
        hostname = request.remote_addr
    returned = Session(
        hostname=hostname,
        product_name=product_name,
        product_revision=product_revision,
        product_version=product_version,
        total_num_tests=total_num_tests,
        user_id=current_user.id,
logical_id=logical_id,
    )
    if metadata is not None:
        for key, value in metadata.items():
            db.session.add(SessionMetadata(session=returned, key=key, metadata_item=value))
    return returned


@API
def report_session_end(id: int, duration: int=None):
    update = {'end_time': get_current_time() if duration is None else Session.start_time + duration}
    if not Session.query.filter(Session.id == id, Session.end_time == None).update(update):
        if Session.query.filter(Session.id == id).count():
            # we have a session, but it already ended
            abort(requests.codes.conflict)
        else:
            abort(requests.codes.not_found)


@API
def report_test_start(session_id: int, name:str=None, test_logical_id: str=None):
    try:
        session = Session.query.filter(Session.id == session_id).one()
    except NoResultFound:
        abort(requests.codes.not_found)
    if session.end_time is not None:
        abort(requests.codes.conflict)
    return Test(session_id=session.id, logical_id=test_logical_id, name=name)


@API
def report_test_end(id: int, duration: (float, int)=None):
    update = {'end_time': get_current_time() if duration is None else Test.start_time + duration}
    test = Test.query.get(id)
    if test is None:
        abort(requests.codes.not_found)
    if test.end_time is not None:
        # we have a test, but it already ended
        abort(requests.codes.conflict)

    test.end_time = get_current_time() if duration is None else test.start_time + duration

    session_update = {'num_finished_tests': Session.num_finished_tests + 1}
    if test.num_failures:
        session_update['num_failed_tests'] = Session.num_failed_tests + 1
    elif test.num_errors:
        session_update['num_error_tests'] = Session.num_error_tests + 1
    elif test.skipped:
        session_update['num_skipped_tests'] = Session.num_skipped_tests + 1

    Session.query.filter(Session.id == test.session_id).update(session_update)


@API
def report_test_skipped(id: int):
    update = {'skipped': True}
    if not Test.query.filter(Test.id == id).update(update):
        if Test.query.filter(Test.id == id).count():
            # we have a test, but it already ended
            abort(requests.codes.conflict)
        else:
            abort(requests.codes.not_found)

@API
def report_test_interrupted(id: int):
    update = {'interrupted': True}
    if not Test.query.filter(Test.id == id).update(update):
        if Test.query.filter(Test.id == id).count():
            # we have a test, but it already ended
            abort(requests.codes.conflict)
        else:
            abort(requests.codes.not_found)

@API
def add_test_error(id: int):
    try:
        test = Test.query.filter(Test.id == id).one()
        test.num_errors = Test.num_errors + 1
    except NoResultFound:
        abort(requests.codes.not_found)


@API
def add_test_failure(id: int):

    try:
        test = Test.query.filter(Test.id == id).one()
        test.num_failures = Test.num_failures + 1
    except NoResultFound:
        abort(requests.codes.not_found)

@API
def set_metadata(entity_type: str, entity_id: int, key: str, value: object):
    model, kwargs = _get_metadata_model(entity_type, entity_id)
    db.session.add(model(key=key, metadata_item=value, **kwargs))
    try:
        db.session.commit()
    except IntegrityError:
        abort(requests.codes.not_found)

@API
def get_metadata(entity_type: str, entity_id: int):
    model, kwargs = _get_metadata_model(entity_type, entity_id)
    return {obj.key: obj.metadata_item
            for obj in model.query.filter_by(**kwargs)}

def _get_metadata_model(entity_type, entity_id):
    if entity_type == 'session':
        return SessionMetadata, {'session_id': entity_id}

    if entity_type == 'test':
        return TestMetadata, {'test_id': entity_id}

    abort(requests.codes.bad_request)

@API
def add_test_metadata(id: int, metadata: dict):
    try:
        test = Test.query.filter(Test.id == id).one()
        test.metadata_objects.append(TestMetadata(metadata_item=metadata))
    except NoResultFound:
        abort(requests.codes.not_found)

@API
def add_session_metadata(id: int, metadata: dict):

    try:
        session = Session.query.filter(Session.id == id).one()
        session.metadata_objects.append(SessionMetadata(metadata_item=metadata))
    except NoResultFound:
        abort(requests.codes.not_found)

@API
def add_test_error_data(id: int, exception: str, exception_type: str, traceback: list, timestamp: (float, int)=None):
    if timestamp is None:
        timestamp = get_current_time()
    try:
        test = Test.query.filter(Test.id == id).one()
        test.errors.append(Error(exception=exception,
                      exception_type=exception_type,
                      traceback=traceback,
                      timestamp=timestamp))
        test.num_errors = Test.num_errors + 1

    except NoResultFound:
        abort(requests.codes.not_found)

@API
def add_session_error_data(id: int, exception: str, exception_type: str, traceback: list, timestamp: (float, int)=None):
    if timestamp is None:
        timestamp = get_current_time()
    try:
        session = Session.query.filter(Session.id == id).one()
        session.errors.append(Error(exception=exception,
                      exception_type=exception_type,
                      traceback=traceback,
                      timestamp=timestamp))

    except NoResultFound:
        abort(requests.codes.not_found)

@API
def set_test_conclusion(id: int, conclusion: str):
    update = {'test_conclusion': conclusion}
    if not Test.query.filter(Test.id == id).update(update):
        abort(requests.codes.not_found)

@API
def edit_session_status(id: int, status: str):
    if status not in ['', 'RUNNING', 'FAILURE', 'SUCCESS']:
        abort(requests.codes.bad_request)
    update = {'edited_status': status}
    if not Session.query.filter(Session.id == id).update(update):
        abort(requests.codes.not_found)

@API
def edit_test_status(id: int, status: str):
    if status not in ['', 'RUNNING', 'SUCCESS', 'SKIPPED', 'FAILURE', 'ERROR', 'INTERRUPTED']:
        abort(requests.codes.bad_request)
    update = {'edited_status': status}
    if not Test.query.filter(Test.id == id).update(update):
        abort(requests.codes.not_found)
