import flux
import pytest

from .utils import raises_not_found, raises_conflict

def test_report_test_start(started_session, started_test, test_name):
    test = started_session.report_test_start(name=test_name)
    assert test is not None


def test_test_session_id(started_session, started_test):
    assert started_test.session_id == started_session.id


def test_cannot_start_test_ended_session(ended_session):
    with raises_conflict():
        ended_session.report_test_start(name='name')


def test_cannot_start_test_nonexistent_session(nonexistent_session):
    with raises_not_found():
        nonexistent_session.report_test_start(name='name')


def test_start_time(started_test):
    assert started_test.start_time == flux.current_timeline.time()


@pytest.mark.parametrize('use_duration', [True, False])
def test_report_test_end(started_test, use_duration):
    duration = 10
    start_time = started_test.start_time
    if use_duration:
        started_test.report_end(duration=duration)
    else:
        flux.current_timeline.sleep(10)
        started_test.report_end()
    started_test.refresh()
    assert started_test.end_time == start_time + duration


def test_end_test_doesnt_exist(nonexistent_test):
    with raises_not_found():
        nonexistent_test.report_end()


def test_end_test_twice(ended_test):
    with raises_conflict():
        ended_test.report_end()
