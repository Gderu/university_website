import datetime
from dateutil import tz

import pytest
from flask import session, json

from flaskr.db import get_db


def test_add_exercise_check(client, auth):
    assert auth.login('333333333', 'secret').status_code == 200

    with client:
        response = client.post('/checks/add-exercise-check', data={'course_id': "000000000-0", 'num_exercises': 25,
                                                                   'description': 'added a few exercises'})
        assert response.status_code == 200

        response = client.post('/checks/add-exercise-check', data={'course_id': "000000000-0", 'num_exercises': 25,
                                                                   'description': 'added a few exercises'})
        assert response.status_code == 403

        response = client.post('/checks/add-exercise-check', data={'course_id': "000000000-1", 'num_exercises': 25,
                                                                   'description': 'added a few exercises'})
        assert response.status_code == 403

        db = get_db()
        result = db.execute('SELECT used_exercises FROM course where id == ?', ("000000000-0",)).fetchone()
        assert result is not None
        assert result[0] == 48

        result = db.execute('SELECT request_open_date, request_close_date FROM exercise_check where id == ?',
                            (1,)).fetchone()
        print(result['request_open_date'])
        date = datetime.datetime.strptime(result['request_open_date'], '%Y-%m-%d %H:%M:%S')
        local_tz_date = date.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())

        assert (datetime.datetime.now(tz.tzlocal()) - local_tz_date).total_seconds() < 10


def test_close_exercise_check(client, auth):
    assert auth.login('333333333', 'secret').status_code == 200

    with client:
        response = client.post('/checks/add-exercise-check', data={'course_id': "000000000-0", 'num_exercises': 1,
                                                                   'description': 'added a few exercises'})
        assert response.status_code == 200
        response = client.post('/checks/add-exercise-check', data={'course_id': "000000000-0", 'num_exercises': 1,
                                                                   'description': 'added a few exercises'})
        assert response.status_code == 200

        assert auth.login('111111111', '321123').status_code == 200
        response = client.post('/checks/close-exercise-check', data={'id': 1, 'accepted': True})
        assert response.status_code == 200
        response = client.post('/checks/close-exercise-check', data={'id': 1, 'accepted': False})
        assert response.status_code == 403
        response = client.post('/checks/close-exercise-check', data={'id': 2, 'accepted': False})
        assert response.status_code == 200

        db = get_db()
        request_close_date, accepted = db.execute('SELECT request_close_date, accepted FROM exercise_check WHERE '
                                                  'id == ?', (1,)).fetchone()

        date = datetime.datetime.strptime(request_close_date, '%Y-%m-%d %H:%M:%S')
        local_tz_date = date.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())

        assert (datetime.datetime.now(tz.tzlocal()) - local_tz_date).total_seconds() < 10
        assert accepted == 1

        request_close_date, accepted = db.execute('SELECT request_close_date, accepted FROM exercise_check WHERE '
                                                  'id == ?', (2,)).fetchone()

        date = datetime.datetime.strptime(request_close_date, '%Y-%m-%d %H:%M:%S')
        local_tz_date = date.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())

        assert (datetime.datetime.now(tz.tzlocal()) - local_tz_date).total_seconds() < 10
        assert accepted == 0


def test_get_exercise_checks(client, auth):
    assert auth.login('333333333', 'secret').status_code == 200

    with client:
        response = client.post('/checks/add-exercise-check', data={'course_id': "000000000-0", 'num_exercises': 1,
                                                                   'description': 'added a few exercises'})
        assert response.status_code == 200
        response = client.post('/checks/add-exercise-check', data={'course_id': "000000000-0", 'num_exercises': 1,
                                                                   'description': 'added a few exercises'})
        assert response.status_code == 200

        auth.login()
        result = client.get('/checks/get-exercise-checks')
        assert result.status_code == 200
        data = json.loads(result.data)['exercise_checks']
        assert len(data) == 2

        assert auth.login('111111111', '321123').status_code == 200
        result = client.get('/checks/get-exercise-checks')
        assert result.status_code == 200
        data = json.loads(result.data)['exercise_checks']
        assert len(data) == 2

        response = client.post('/checks/close-exercise-check', data={'id': 1, 'accepted': True})
        assert response.status_code == 200

        result = client.get('/checks/get-exercise-checks')
        assert result.status_code == 200
        data = json.loads(result.data)['exercise_checks']
        assert len(data) == 1
