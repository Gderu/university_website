import datetime
from dateutil import tz

from flask import (
    Blueprint, session, request
)

from flaskr.db import get_db
from flaskr.auth import login_required, Permissions

INCORRECT_VALUES = {"error": "נתונים לא נכונים"}, 400

bp = Blueprint('checks', __name__, url_prefix='/checks')


@bp.route('/add-exercise-check', methods=['POST'])
@login_required
def add_exercise_check():
    if Permissions(session['user']['role']) != Permissions.CHECKER:
        return {'error': 'רק בודק יכול לפתוח בקשת בדיקה'}, 403

    try:
        course_id = request.form['course_id']
        num_exercises = request.form['num_exercises']
        description = request.form['description']
    except KeyError:
        return INCORRECT_VALUES

    if not num_exercises.isdigit():
        return INCORRECT_VALUES
    num_exercises = int(num_exercises)

    db = get_db()
    result = db.execute('SELECT 1 FROM user_course_privileges WHERE user_id == ? AND course_id == ?',
                        (session['user']['id'], course_id)).fetchone()
    if result is None:
        return {'error': 'למשתמש אין הרשאות לקורס זה'}, 403

    result = db.execute('SELECT num_exercises, used_exercises FROM course WHERE id == ?', (course_id,)).fetchone()
    if result is None:
        return {'error': 'מזהה קורס לא נמצא'}, 404
    max_exercises, used_exercises = result
    if used_exercises + num_exercises > max_exercises:
        return {'error': 'לא נותרו מספיק בדיקות לקורס זה'}, 403

    db.execute('INSERT INTO exercise_check(course_id, checker_id, num_exercises, description) '
               'VALUES(?, ?, ?, ?)', (course_id, session['user']['id'], num_exercises, description))
    db.execute('UPDATE course SET used_exercises = used_exercises + ? WHERE id == ?', (num_exercises, course_id))
    db.commit()
    return {}, 200


@bp.route('/close-exercise-check', methods=['POST'])
@login_required
def close_exercise_check():
    if Permissions(session['user']['role']) == Permissions.CHECKER:
        return {'error': 'רק מרצה יכול לסגור בקשת בדיקה'}, 403

    try:
        id = request.form['id']
        accepted = request.form['accepted']
    except KeyError:
        return INCORRECT_VALUES

    if not id.isdigit() or accepted not in ["False", "True"]:
        return INCORRECT_VALUES

    id = int(id)
    accepted = accepted == "True"

    db = get_db()
    exists = db.execute('SELECT accepted FROM exercise_check WHERE id == ?', (id,)).fetchone()
    if exists is None:
        return {"error": "מזהה בקשה לא נמצא"}, 404
    if exists[0] is not None:
        return {"error": "בקשה כבר סגורה"}, 403

    if accepted:
        date_utc = datetime.datetime.now().astimezone(tz.UTC).strftime('%Y-%m-%d %H:%M:%S')
        db.execute('UPDATE exercise_check SET request_close_date = ?, accepted = ? WHERE id == ?',
                   (date_utc, accepted, id))
    else:
        course_id, num_exercises = db.execute('SELECT course_id, num_exercises FROM exercise_check WHERE id == ?',
                                              (id,)).fetchone()
        date_utc = datetime.datetime.now().astimezone(tz.UTC).strftime('%Y-%m-%d %H:%M:%S')
        db.execute('UPDATE exercise_check SET request_close_date = ?, accepted = ? WHERE id == ?',
                   (date_utc, accepted, id))
        db.execute('UPDATE course SET used_exercises = used_exercises - ? WHERE id == ?', (num_exercises, course_id))
    db.commit()
    return {}, 200


@bp.route('/get-exercise-checks', methods=['GET'])
@login_required
def get_exercise_checks():
    db = get_db()
    if Permissions(session['user']['role']) == Permissions.ADMIN:
        results = db.execute('SELECT * FROM exercise_check WHERE accepted IS NULL').fetchall()
        print("IN")
    else:
        course_ids = db.execute('SELECT course_id FROM user_course_privileges WHERE user_id == ?',
                                (session['user']['id'],)).fetchall()
        if len(course_ids) == 0:
            return {'exercise_checks': []}, 200
        course_ids = [course_id[0] for course_id in course_ids]
        sqlite_request = 'SELECT * FROM exercise_check WHERE accepted IS NULL AND ' + 'course_id == ? OR ' * len(course_ids)
        sqlite_request = sqlite_request[:-4]
        results = db.execute(sqlite_request, course_ids).fetchall()
    results = [dict(row) for row in results]
    return {'exercise_checks': results}, 200
