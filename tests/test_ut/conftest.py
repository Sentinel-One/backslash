import math
from uuid import uuid1

import flux

import pytest



@pytest.fixture(autouse=True, scope='session')
def freeze_timeline(request):

    original_factor = flux.current_timeline.get_time_factor()

    @request.addfinalizer
    def finalizer():
        flux.current_timeline.set_time_factor(original_factor)

    flux.current_timeline.set_time_factor(0)
    current_time = flux.current_timeline.time()
    next_round_time = math.ceil(current_time * 10000) / 10000.0
    flux.current_timeline.sleep(next_round_time - current_time)


@pytest.fixture(params=[('name',), ('name', 'version'), ('name', 'version', 'revision')])
def product_info(request):
    included_field_names = request.param
    info = {'name': 'foo', 'version': 'bar', 'revision': 'qux'}
    return dict((field_name, info[field_name]) for field_name in included_field_names)

@pytest.fixture
def started_session(client):
    return client.report_session_start()


@pytest.fixture
def ended_session(client):
    # we don't use started_session to enable tests to use both...
    session = client.report_session_start()
    session.report_end()
    return session


@pytest.fixture
def nonexistent_session(client):
    from backslash.session import Session
    return Session(client, {'id': 238723287, 'type': 'session'})


@pytest.fixture
def test_name():
    return 'test_{0}'.format(uuid1())


@pytest.fixture
def started_test(started_session, test_name):
    return started_session.report_test_start(name=test_name, test_logical_id='11')

@pytest.fixture
def started_session_with_ended_test(started_session, test_name):
    test = started_session.report_test_start(name=test_name, test_logical_id='11')
    test.report_end()
    return (started_session, test)

@pytest.fixture
def ended_test(started_session, test_name):
    returned = started_session.report_test_start(name=test_name, test_logical_id='11')
    returned.report_end()
    return returned


@pytest.fixture
def nonexistent_test(client, started_session):
    from backslash.test import Test
    return Test(client, {'id': 6666, 'session_id': started_session.id, 'logical_id': '6677'})


@pytest.fixture
def logical_id():
    return 'my_logical_id'


@pytest.fixture
def error_data():
    data = {
        'exception': 'assert (2 + 2) == 5',
        'exception_type': 'AssertionError',
        'traceback': [{'filename': 'foo.py', 'lineno': 100, 'func_name': 'foo', 'locals': [], 'globals': [],
                          'code_line': 'line of code', 'code_string': 'lots of lines of code'},
                      {'filename': 'bar.py', 'lineno': 200, 'func_name': 'bar', 'locals': [], 'globals': [],
                          'code_line': 'line of code', 'code_string': 'lots of lines of code'}]
    }
    return data

@pytest.fixture
def metadata_key():
    return 'metadata_key'

@pytest.fixture(params=[1, 'hey', 2.0, True, None])
def metadata_value(request):
    return request.param


@pytest.fixture(params=['session', 'test'])
def metadata_holder(request, client):
    session = client.report_session_start()
    if request.param == 'session':
        return session
    test = session.report_test_start()
    return test




