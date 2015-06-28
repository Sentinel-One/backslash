from contextlib import contextmanager

import requests

import pytest

from flask_app import models


def raises_conflict():
    return raises_http_error(requests.codes.conflict)


def raises_bad_request():
    return raises_http_error(requests.codes.bad_request)


def raises_not_found():
    return raises_http_error(requests.codes.not_found)

@contextmanager
def raises_http_error(status_code):
    with pytest.raises(requests.HTTPError) as caught:
        yield
    assert caught.value.response.status_code == status_code

def model_for(backslash_client_obj):
    # not supported
    assert backslash_client_obj.type == 'session'
    return models.Session.query.get(backslash_client_obj.id)
