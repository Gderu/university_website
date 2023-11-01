import json

import pytest
from flask import session, json
from flaskr.db import get_db
from werkzeug.security import check_password_hash


@pytest.mark.parametrize(('id', 'name', 'points', 'num_students', 'num_exercises',
                          'used_exercises', 'semester_name', 'should_fail'), (
        ('1-1', 'אינפי 1', 5.5, 20, 50, 0, 'אביב 2024', False),
        ('1-2', 'אינפי 1', 5.5, 20, 50, 55, 'אביב 2024', True),
        ('1-2', 'אינפי 1', 5.5, 20, 50, 0, 'אבי 2024', True),
        ('1-2', 'אינפי 2', 10, 20, 50, 0, 'אביב 2024', False),
        ('1-3', 'אינפי 3', 10, -20, 50, 0, 'אביב 2024', True),
))
def test_add_course(auth, client, id, name, points, num_students, num_exercises,
                    used_exercises, semester_name, should_fail):
    data = {
        'id': id,
        'name': name,
        'points': points,
        'num_students': num_students,
        'num_exercises': num_exercises,
        'used_exercises': used_exercises,
        'semester_name': semester_name,
    }
    with client:
        auth.login()
        response = client.post('/admin/add-course', data=data)
        if should_fail:
            assert response.status_code != 200
        else:
            assert response.status_code == 200
            db = get_db()
            course = db.execute("SELECT * FROM course WHERE id = ?", (id,)).fetchone()
            assert dict(course) == data


def test_add_course_twice(auth, client):
    data = {'id': 1-1,
            'name': 'אינפי 1',
            'points': 5.5,
            'num_students': 20,
            'num_exercises': 50,
            'used_exercises': 0,
            'semester_name': 'אביב 2024'}
    with client:
        auth.login()
        response = client.post('/admin/add-course', data=data)
        assert response.status_code == 200
        response = client.post('/admin/add-course', data=data)
        assert response.status_code == 403


def test_update_course(auth, client):
    data = {'id': '1-1',
            'name': 'אינפי 1',
            'points': 5.5,
            'num_students': 20,
            'num_exercises': 50,
            'used_exercises': 0,
            'semester_name': 'אביב 2024'}
    auth.login()

    with client:
        response = client.post('/admin/add-course', data=data)
        assert response.status_code == 200
        response = client.put('/admin/update-course', data={'id': '1-1', 'name': 'אינפי 2'})
        assert response.status_code == 200
        db = get_db()
        name = db.execute("SELECT name FROM course WHERE id = ?", (data['id'],)).fetchone()[0]
        assert name == 'אינפי 2'
        response = client.put('/admin/update-course', data={'id': '2-1', 'name': 'אינפי 2'})
        assert response.status_code == 404


def test_delete_course(auth, client):
    data = {'id': '1-1',
            'name': 'אינפי 1',
            'points': 5.5,
            'num_students': 20,
            'num_exercises': 50,
            'used_exercises': 0,
            'semester_name': 'אביב 2024'}

    auth.login()

    with client:
        response = client.post('/admin/add-course', data=data)
        assert response.status_code == 200
        response = client.post('/admin/delete-course', data={'id': '1-1'})
        assert response.status_code == 200
        response = client.post('/admin/delete-course', data={'id': '1-1'})
        assert response.status_code == 404

        db = get_db()
        assert db.execute("SELECT name FROM course WHERE id = ?", (data['id'],)).fetchone() is None


@pytest.mark.parametrize(('id', 'password', 'name', 'mail', 'role', 'is_student', 'should_fail'), (
        ('111111112', 'hello world', 'Orr Sharon', 'orr.sharon.orr@gmail.com', '2', '1', False),
        ('111111112', 'hello world', 'Orr Sharon', 'orr.sharon.orr@gmail.com', '2', '2', True),
        ('111111112', 'hello world', 'Orr Sharon', 'orr.sharon.orr@gmail.com', '3', '1', True),
        ('111111112', 'hello world', 'Orr Sharon', 'orr.sharon.orrgmail.com', '2', '1', True),
        ('111111112', 'hello world', '', 'orr.sharon.orr@gmail.com', '2', '1', True),
        ('111111112', 'hello', 'Orr Sharon', 'orr.sharon.orr@gmail.com', '2', '1', True),
))
def test_add_user(auth, client, id, password, name, mail, role, is_student, should_fail):
    data = {
        'id': id,
        'password': password,
        'name': name,
        'mail': mail,
        'role': role,
        'is_student': is_student,
    }
    with client:
        auth.login()
        response = client.post('/admin/add-user', data=data)
        if should_fail:
            assert response.status_code != 200
        else:
            assert response.status_code == 200
            db = get_db()
            course = db.execute("SELECT * FROM user_data WHERE id = ?", (id,)).fetchone()
            course_check = {key: str(val) for key, val in dict(course).items() if key != 'password'}
            data_check = {key: val for key, val in data.items() if key != 'password'}
            assert course_check == data_check
            assert check_password_hash(course['password'], data['password'])


def test_update_user(auth, client):
    data = {
        'id': '111111112',
        'password': 'hello world',
        'name': 'Orr Sharon',
        'mail': 'orr.sharon.orr@gmail.com',
        'role': '2',
        'is_student': '1'
    }
    auth.login()

    with client:
        response = client.post('/admin/add-user', data=data)
        assert response.status_code == 200
        response = client.put('/admin/update-user', data={'id': data['id'], 'name': 'Golda Meir'})
        print(json.loads(response.data))
        assert response.status_code == 200
        db = get_db()
        name = db.execute("SELECT name FROM user_data WHERE id = ?", (data['id'],)).fetchone()[0]
        assert name == 'Golda Meir'
        response = client.put('/admin/update-user', data={'id': '111111113', 'name': 'God'})
        assert response.status_code == 404


def test_delete_course(auth, client):
    data = {
        'id': '111111112',
        'password': 'hello world',
        'name': 'Orr Sharon',
        'mail': 'orr.sharon.orr@gmail.com',
        'role': '2',
        'is_student': '1'
    }

    auth.login()

    with client:
        response = client.post('/admin/add-user', data=data)
        assert response.status_code == 200
        response = client.post('/admin/delete-user', data={'id': data['id']})
        assert response.status_code == 200
        response = client.post('/admin/delete-user', data={'id': data['id']})
        assert response.status_code == 404

        db = get_db()
        assert db.execute("SELECT name FROM user_data WHERE id = ?", (data['id'],)).fetchone() is None


def test_add_user_course(auth, client):
    auth.login()

    with client:
        response = client.post('/admin/add-user-course', data={'user_id': '222222222', 'course_id': '000000000-0'})
        assert response.status_code == 200
        response = client.post('/admin/add-user-course', data={'user_id': '222222222', 'course_id': '000000000-0'})
        assert response.status_code == 403
        response = client.post('/admin/add-user-course', data={'user_id': '111111112', 'course_id': '000000000-0'})
        assert response.status_code == 404
        response = client.post('/admin/add-user-course', data={'user_id': '222222222', 'course_id': '000000000-2'})
        assert response.status_code == 404


def test_delete_user_course(auth, client):
    auth.login()

    with client:
        response = client.post('/admin/add-user-course', data={'user_id': '222222222', 'course_id': '000000000-0'})
        assert response.status_code == 200
        response = client.post('/admin/delete-user-course', data={'user_id': '111111111', 'course_id': '000000000-0'})
        assert response.status_code == 200
        response = client.post('/admin/delete-user-course', data={'user_id': '111111111', 'course_id': '000000000-0'})
        assert response.status_code == 404


def test_get_users(auth, client):
    auth.login()

    with client:
        response = client.get('/admin/get-users')
        assert response.status_code == 200
        assert len(json.loads(response.data)['users']) == 4
