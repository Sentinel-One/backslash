import datetime

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.orm import backref

from .app import app
from .utils import get_current_time
from .rendering import computed_field

from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy(app)


class Session(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    logical_id = db.Column(db.String(256), index=True)
    start_time = db.Column(db.Float, default=get_current_time)
    end_time = db.Column(db.Float, default=None)
    hostname = db.Column(db.String(100))
    product_name = db.Column(db.String(256), index=True)
    product_version = db.Column(db.String(256), index=True)
    product_revision = db.Column(db.String(256), index=True)
    user_name = db.Column(db.String(256), index=True)
    tests = db.relationship('Test', backref=backref('session'), cascade='all, delete, delete-orphan')

    # test counts
    num_failed_tests = db.Column(db.Integer, default=0)
    num_error_tests = db.Column(db.Integer, default=0)
    num_skipped_tests = db.Column(db.Integer, default=0)
    num_finished_tests = db.Column(db.Integer, default=0)

    @computed_field
    def status(self):
        if self.end_time is None:
            return 'RUNNING'
        else:
            for test in self.tests:
                if test.status() == 'FAILURE' or test.status() == 'ERROR':
                    return 'FAILURE'
            return 'SUCCESS'


class Test(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), index=True)
    logical_id = db.Column(db.String(256), index=True)
    start_time = db.Column(db.Float, default=get_current_time)
    end_time = db.Column(db.Float, default=None)
    name = db.Column(db.String(256), index=True)
    skipped = db.Column(db.Boolean, default=False)
    interrupted = db.Column(db.Boolean, default=False)
    num_errors = db.Column(db.Integer, default=0)
    num_failures = db.Column(db.Integer, default=0)
    metadata_objects = db.relationship('TestMetadata', backref=backref('test'), cascade='all, delete, delete-orphan')

    @computed_field
    def duration(self):
        if self.end_time is None or self.start_time is None:
            return None
        return self.end_time - self.start_time

    @computed_field
    def status(self):
        if self.interrupted:
            return 'INTERRUPTED'
        if self.end_time is None:
            return 'RUNNING'
        else:
            if self.skipped:
                return 'SKIPPED'
            if self.num_failures > 0:
                return 'FAILURE'
            elif self.num_errors > 0:
                return 'ERROR'
        return 'SUCCESS'

    @computed_field
    def test_metadata(self):
        combined_json_object = {}
        for metadata_object in self.metadata_objects:
            for key, value in metadata_object.metadata_item.iteritems():
                combined_json_object[key] = value
        return combined_json_object


class TestMetadata(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id', ondelete='CASCADE'), index=True)
    metadata_item = db.Column(JSONB)
