import json

import pytest
from flask import session, json
from flaskr.db import get_db
from werkzeug.security import check_password_hash


def test_get_courses(auth, client):
    with client:
        auth.login()
        response = client.get('/data/get-courses')
        assert response.status_code == 200
        data = json.loads(response.data)['courses']
        assert len(data) == 2

        client.post('/admin/add-course', data={
            'id': '1-1',
            'name': 'אינפי 1',
            'points': 5.5,
            'num_students': 20,
            'num_exercises': 50,
            'used_exercises': 0,
            'semester_name': 'אביב 2024',
        })
        response = client.get('/data/get-courses')
        assert response.status_code == 200
        data = json.loads(response.data)['courses']
        assert len(data) == 3
        auth.login('111111111', '321123')
        response = client.get('/data/get-courses')
        assert response.status_code == 200
        data = json.loads(response.data)['courses']
        assert len(data) == 1
        response = client.get('/data/get-courses', data={'semester': 'קיץ 2024'})
        assert response.status_code == 200
        data = json.loads(response.data)['courses']
        assert len(data) == 0


def test_get_users(auth, client):
    with client:
        auth.login()
        response = client.get('/data/get-users')
        assert response.status_code == 200
        data = json.loads(response.data)['users']
        print(data)
        assert len(data) == 4
        assert 1 == 0
