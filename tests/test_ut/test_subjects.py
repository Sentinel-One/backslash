import pytest

from .utils import model_for

def test_add_subject(started_session, subjects, flask_app):
    started_session.add_subject(**subjects[0])

    with flask_app.app_context():
        session = model_for(started_session)
        assert len(session.subjects) == 1
        assert session.subjects[0].subject.name == subjects[0]['name']
        assert session.subjects[0].revision.product_version.product.name == subjects[0]['product']

@pytest.mark.parametrize('field_name', ['product', 'version', 'revision'])
def test_add_subject_deduplication(started_session, flask_app, field_name):
    first_subject = {'name': 'some_subject', 'product': 'car', 'version': '1', 'revision': 'a'}
    started_session.add_subject(**first_subject)
    second_subject = first_subject.copy()
    second_subject[field_name] = 'new_field_value'
    started_session.add_subject(**second_subject)

    with flask_app.app_context():
        session = model_for(started_session)
        assert len(session.subjects) == 2
        s1, s2 = session.subjects
        prod1, prod2 = map(lambda x: x.revision.product_version.product.id, session.subjects)
        ver1, ver2 = map(lambda x: x.revision.product_version.id, session.subjects)
        rev1, rev2 = map(lambda x: x.revision.id, session.subjects)

        if field_name == 'product':
            assert prod1 != prod2
            assert ver1 != ver2
            assert rev1 != rev2
        elif field_name == 'version':
            assert prod1 == prod2
            assert ver1 != ver2
            assert rev1 != rev2
        elif field_name == 'revision':
            assert prod1 == prod2
            assert ver1 == ver2
            assert rev1 != rev2
        else:
            raise NotImplementedError() # pragma: no cover
