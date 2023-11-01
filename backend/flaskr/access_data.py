from collections import defaultdict

from flask import (
    Blueprint, session, request
)

from flaskr.db import get_db
from flaskr.auth import login_required, Permissions

INCORRECT_VALUES = {"error": "נתונים לא נכונים"}, 400

bp = Blueprint('access_data', __name__, url_prefix='/data')

# TODO might need to redo this, need to see how frontend turns out


@bp.route('/get-courses', methods=['GET'])
@login_required
def get_courses():
    if 'semester' in request.form:
        session['user']['semester'] = request.form['semester']

    db = get_db()
    if Permissions(session['user']['role']) == Permissions.ADMIN:
        results = db.execute('SELECT * FROM course WHERE semester_name == ?', (session['user']['semester'],)).fetchall()
    else:
        course_ids = db.execute('SELECT course_id FROM user_course_privileges WHERE user_id == ?',
                                (session['user']['id'],)).fetchall()
        if len(course_ids) == 0:
            return {'courses': []}, 200
        course_ids = [course_id[0] for course_id in course_ids]
        sqlite_request = 'SELECT * FROM course WHERE semester_name == ? AND (' + 'id == ? OR ' * len(course_ids)
        sqlite_request = sqlite_request[:-4] + ')'
        results = db.execute(sqlite_request, [session['user']['semester'], *course_ids]).fetchall()
    results = [dict(row) for row in results]
    return {'courses': results}, 200


@bp.route('/get-users', methods=['GET'])
@login_required
def get_users():
    if 'semester' in request.form:
        session['user']['semester'] = request.form['semester']

    db = get_db()
    results = db.execute(
        'SELECT * FROM user_course_privileges WHERE user_id == ?',
        (session['user']['id'],)).fetchall()

    if len(results) == 0:
        return {'users': []}, 200
    user_courses = defaultdict(lambda: [])

    for privilege in results:
        user_courses[privilege['user_id']].append(privilege['course_id'])
    if Permissions(session['user']['role']) == Permissions.ADMIN:
        sqlite_request = 'SELECT * FROM user_data WHERE '
    else:
        sqlite_request = 'SELECT id, name, mail, role, is_student FROM user_data WHERE '

    sqlite_request += 'id == ? OR ' * len(user_courses)
    sqlite_request = sqlite_request[:-4]
    results = db.execute(sqlite_request, list(user_courses.keys())).fetchall()
    complete_user_data = []
    for user in results:
        dict_user = dict(user)
        dict_user['courses'] = user_courses[dict_user['id']]
        complete_user_data.append(dict_user)

    return {'users': complete_user_data}, 200


@bp.route('/get_semesters', methods=['GET'])
@login_required
def get_semesters():
    db = get_db()
    if Permissions(session['user']['role']) == Permissions.ADMIN:
        result = db.execute('SELECT * FROM semester ORDER BY created_at DESC').fetchall()
    else:
        course_ids = db.execute('SELECT course_id FROM user_course_privileges WHERE user_id == ?',
                                (session['user']['id'],)).fetchall()
        if len(course_ids) == 0:
            return [], 200

        course_ids = [course_id[0] for course_id in course_ids]
        ids = ' OR '.join(['id == ?'] * len(course_ids))
        semesters = db.execute('SELECT semester_name FROM course WHERE ' + ids, (course_ids,)).fetchall()
        semesters = set(semester[0] for semester in semesters)
        semester_names = ' OR '.join(['name == ?'] * len(semesters))
        result = db.execute('SELECT semester_name FROM course WHERE ' + ids +
                            ' ORDER BY created_at DESC', (semester_names,)).fetchall()
    result = [name[0] for name in result]
    return result, 200
