import datetime

import flux
from flask import Blueprint, request

from weber_utils import Optional, takes_schema_args

from .api_utils import auto_add_object, get_api_decorator
from .models import db, Session

blueprint = Blueprint('api', __name__)

api_func = get_api_decorator(blueprint)

##########################################################################


@api_func
@auto_add_object
@takes_schema_args(hostname=Optional(str))
def report_session_start(hostname=None):
    if hostname is None:
        hostname = request.remote_addr
    return Session(hostname=hostname, start_time=_now())

@api_func
@takes_schema_args(id=int, duration=Optional((float, int)))
def report_session_end(id, duration=None):
    update = {'end_time': _now() if duration is None else Session.start_time + datetime.timedelta(seconds=duration)}
    Session.query.filter(Session.id==id, Session.end_time==None).update(update)
    db.session.commit()

def _now():
    return datetime.datetime.utcfromtimestamp(flux.current_timeline.time())
