import re

from flask import (
    Blueprint, session, request
)
from werkzeug.security import generate_password_hash
import logging

from flaskr.db import get_db
from flaskr.auth import admin_required, Permissions

PASSWORD_LENGTH = 6
INCORRECT_VALUES = {"error": "נתונים לא נכונים"}, 400

logger = logging.getLogger(__name__)
bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/start-semester', methods=['POST'])
@admin_required
def start_semester():
    pass


@bp.route('/add-course', methods=['POST'])
@admin_required
def add_course(course_data=None):
    if course_data is None:
        course_data = request.form
    try:
        num_students = course_data['num_students']
        num_exercises = course_data['num_exercises']
        used_exercises = course_data['used_exercises']
        points = course_data['points']
        semester_name = course_data['semester_name']
        id = course_data['id']
        name = course_data['name']
        lecturer_id = course_data['id']
    except KeyError:
        return {"error": "בקשה לא תקינה"}, 400

    if not num_students.isdigit() or not num_exercises.isdigit() or not used_exercises.isdigit() \
            or int(num_exercises) < int(used_exercises) or not re.fullmatch(r'[0-9]*(\.[0-9]+)|[0-9]+', points):
        return INCORRECT_VALUES

    db = get_db()
    result = db.execute('SELECT name FROM semester WHERE name == ?',
                                                   (semester_name,)).fetchone()
    if result is None:
        return {"error": "סמסטר לא תקין"}, 400

    result = db.execute('SELECT role FROM user_data WHERE id == ?', (lecturer_id,)).fetchone()
    if result is None or Permissions(result[0]) != Permissions.LECTURER:
        return {"error": "מזהה מרצה לא תקין"}, 403

    try:
        db.execute(
            'INSERT INTO course (id, name, points, num_students, num_exercises, '
            'used_exercises, semester_name, lecturer_id)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (id, name, float(points), int(num_students), int(num_exercises),
             int(used_exercises), semester_name, lecturer_id)
        )
        db.commit()
    except db.IntegrityError as e:
        if 'lecturer_id' in str(e):
            return {"error": "מזהה מרצה זה לא קיים במערכת"}, 404
        else:
            return {"error": "קורס עם מספר זה כבר קיים במערכת"}, 403
    return {}, 200


@bp.route('/update-course', methods=['PUT'])
@admin_required
def update_course(new_course_data=None):
    if new_course_data is None:
        new_course_data = dict(request.form)
    if 'id' not in new_course_data:
        return INCORRECT_VALUES

    db = get_db()
    course = db.execute(
        'SELECT * FROM course WHERE id = ?',
        (new_course_data['id'],)
    ).fetchone()
    if course is None:
        return {"error": "קורס לא נמצא"}, 404

    course = dict(course)
    # updating the course data
    for key in new_course_data:
        if key not in course:
            print(key)
            return INCORRECT_VALUES
        course[key] = new_course_data[key]

    course = {key: str(val) for key, val in course.items()}
    print(course)
    if not course['num_students'].isdigit() or not course['num_exercises'].isdigit() \
            or not course['used_exercises'].isdigit() \
            or int(course['num_exercises']) < int(course['used_exercises']) \
            or not re.fullmatch(r'[0-9]*(\.[0-9]+)|[0-9]+', course['points']):
        return INCORRECT_VALUES

    result = db.execute('SELECT name FROM semester WHERE name == ?',
                        (course['semester_name'],)).fetchone()
    if result is None:
        return {"error": "סמסטר לא תקין"}, 400

    result = db.execute('SELECT role FROM user_data WHERE id == ?', (course['lecturer_id'],)).fetchone()
    if result is None or Permissions(result[0]) != Permissions.LECTURER:
        return {"error": "מזהה מרצה לא תקין"}, 403

    try:
        db.execute(
            'UPDATE course SET name = ?, points = ?, num_students = ?, '
            'num_exercises = ?, used_exercises = ?, semester_name = ?, lecturer_id = ? WHERE id == ?',
            (course['name'], float(course['points']), int(course['num_students']), int(course['num_exercises']),
             int(course['used_exercises']), course['semester_name'], course['lecturer_id'], course['id'])
        )
        db.commit()
    except db.IntegrityError:
        return INCORRECT_VALUES
    return {}, 200


@bp.route('/delete-course', methods=['POST'])
@admin_required
def delete_course(to_delete=None):
    if to_delete is None:
        try:
            to_delete = request.form['id']
        except KeyError:
            return INCORRECT_VALUES

    db = get_db()
    exists = db.execute('SELECT 1 FROM course WHERE id = ?', (to_delete,)).fetchone()
    if not exists:
        return {"error": "קורס לא נמצא"}, 404

    db.execute('DELETE FROM course WHERE id = ?', (to_delete,))
    db.commit()
    return {}, 200


@bp.route('/add-batch-courses', methods=['POST'])
@admin_required
def add_batch_courses():
    pass


@bp.route('/add-user', methods=['POST'])
@admin_required
def add_user(user_data=None):
    if user_data is None:
        user_data = request.form
    try:
        user_id = user_data['id']
        password = user_data['password']
        name = user_data['name']
        mail = user_data['mail']
        role = user_data['role']
        is_student = user_data['is_student']
    except KeyError:
        return INCORRECT_VALUES

    if not user_id or not user_id.isdigit() or not len(user_id) == 9:
        return {"error": "תעודת הזהות חייבת להיות בת 9 ספרות"}, 400
    if len(password) < PASSWORD_LENGTH:
        return {"error": "הסיסמה חייבת להיות בת 6 תווים לפחות"}, 400
    if len(name) == 0:
        return {"error": "דרוש שם תקני"}, 400
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", mail):
        return {"error": "אנא הכנס מייל תקני"}, 400
    if not role.isdigit() or int(role) not in [0, 1, 2] or not is_student.isdigit() or int(is_student) not in [0, 1]:
        return INCORRECT_VALUES

    db = get_db()
    try:
        db.execute(
            "INSERT INTO user_data (id, password, name, mail, role, is_student) VALUES (?, ?, ?, ?, ?, ?)",
            (int(user_id), generate_password_hash(password), name, mail, int(role), bool(int(is_student))),
        )
        db.commit()
    except db.IntegrityError as e:
        if 'user.mail' in str(e):
            return {"error": "המייל כבר קיים במערכת"}, 403
        elif 'user.id' in str(e):
            return {"error": "המשתמש כבר קיים במערכת"}, 403
        else:
            logger.error(str(e))
            return {"error": "שגיאת שרת"}, 500
    else:
        return {}, 200


@bp.route('/update-user', methods=['PUT'])
@admin_required
def update_user(user_data=None):
    if user_data is None:
        user_data = request.form

    if user_data.get('id') is None or not user_data['id'].isdigit() or len(user_data['id']) != 9:
        return {"error": "תעודת הזהות חייבת להיות בת 9 ספרות"}, 400

    db = get_db()
    user = db.execute(
        'SELECT * FROM user_data WHERE id = ?',
        (int(user_data['id']),)
    ).fetchone()
    if user is None:
        return {"error": "משתמש לא נמצא"}, 404

    user = {key: str(val) for key, val in dict(user).items()}

    # updating the course data
    for key in user_data:
        if key not in user:
            print(key)
            print(user)
            return INCORRECT_VALUES
        user[key] = user_data[key]

    if len(user['password']) < PASSWORD_LENGTH:
        return {"error": "הסיסמה חייבת להיות בת 6 תווים לפחות"}, 400
    if len(user['name']) == 0:
        return {"error": "דרוש שם תקני"}, 400
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", user['mail']):
        return {"error": "אנא הכנס מייל תקני"}, 400
    if not user['role'].isdigit() or int(user['role']) not in [0, 1, 2] or not user['is_student'].isdigit() or \
            int(user['is_student']) not in [0, 1]:
        return INCORRECT_VALUES

    db = get_db()
    try:
        db.execute(
            "UPDATE user_data SET password = ?, name = ?, mail = ?, role = ?, is_student = ? WHERE id == ?",
            (generate_password_hash(user['password']), user['name'], user['mail'],
             int(user['role']), bool(int(user['is_student'])), int(user['id']), ),
        )
        db.commit()
    except db.IntegrityError as e:
        if 'user.mail' in str(e):
            return {"error": "המייל כבר קיים במערכת"}, 403
        else:
            logger.error(str(e))
            return {"error": "שגיאת שרת"}, 500
    else:
        return {}, 200


@bp.route('/delete-user', methods=['POST'])
@admin_required
def delete_user(to_delete=None):
    if to_delete is None:
        try:
            to_delete = request.form['id']
        except KeyError:
            return INCORRECT_VALUES

    if not to_delete.isdigit() or len(to_delete) != 9:
        return INCORRECT_VALUES

    db = get_db()
    exists = db.execute('SELECT 1 FROM user_data WHERE id = ?', (int(to_delete),)).fetchone()
    if not exists:
        return {"error": "משתמש לא נמצא"}, 404

    db.execute('DELETE FROM user_data WHERE id = ?', (int(to_delete),))
    db.commit()
    return {}, 200


@bp.route('/add-user-course', methods=['POST'])
@admin_required
def add_user_course(user_data=None):
    if user_data is None:
        user_data = request.form
    try:
        user_id = user_data['user_id']
        course_id = user_data['course_id']
    except KeyError:
        return INCORRECT_VALUES

    if not user_id.isdigit():
        return INCORRECT_VALUES

    db = get_db()
    try:
        db.execute('INSERT INTO user_course_privileges(user_id, course_id) '
                   'VALUES (?, ?)',
                   (int(user_id), course_id))
        db.commit()
    except db.IntegrityError as e:
        if 'UNIQUE' in str(e):
            return {'error': 'קשר זה כבר קיים במערכת'}, 403
        else:
            if db.execute('SELECT 1 FROM user_data WHERE id == ?', (int(user_id),)).fetchone() is None:
                return {'error': 'קורס זה אינו קיים במערכת'}, 404
            else:
                return {'error': 'משתמש זה אינו קיים במערכת'}, 404

    return {}, 200


@bp.route('/delete-user-course', methods=['POST'])
@admin_required
def delete_user_course(to_delete=None):
    if to_delete is None:
        to_delete = request.form
    try:
        user_id = to_delete['user_id']
        course_id = to_delete['course_id']
    except KeyError:
        return INCORRECT_VALUES

    if not user_id.isdigit():
        return INCORRECT_VALUES

    db = get_db()
    if db.execute('SELECT * FROM user_course_privileges WHERE user_id == ? AND course_id == ?', (int(user_id), course_id)).fetchone() is None:
        return {"error": "ערך זה לא נמצא במאגר מידע"}, 404

    db.execute('DELETE FROM user_course_privileges WHERE user_id == ? AND course_id == ?',
               (int(user_id), course_id))
    db.commit()
    return {}, 200


@bp.route('/add-batch_users', methods=['POST'])
@admin_required
def add_batch_users():
    pass


@bp.route('/get-users', methods=['GET'])
@admin_required
def get_users():
    db = get_db()
    users = db.execute('SELECT * FROM user_data', ).fetchall()
    return {'users': [dict(row) for row in users]}, 200