import functools
import re
from enum import Enum
import logging
from flask import (
    Blueprint, session, request
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


PASSWORD_LENGTH = 6
INCORRECT_VALUES = {"error": "נתונים לא נכונים"}, 400


class Permissions(Enum):
    ADMIN = 0
    LECTURER = 1
    CHECKER = 2


bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view1(**kwargs):
        if session.get('user') is None:
            return {"error": "לא קיימות הרשאות מתאימות לפעולה זו"}, 403

        return view(**kwargs)

    return wrapped_view1


def admin_required(view):
    @login_required
    @functools.wraps(view)
    def wrapped_view2(**kwargs):
        if Permissions(session['user']['role']) != Permissions.ADMIN:
            return {"error": "לא קיימות הרשאות מתאימות לפעולה זו"}, 403

        return view(**kwargs)

    return wrapped_view2


@bp.route('/login', methods=['POST'])
def login():
    try:
        user_id = request.form['user_id']
        password = request.form['password']
    except KeyError:
        return INCORRECT_VALUES

    incorrect_credentials = {"error": "שם משתמש או סיסמה שגויים"}, 403

    if not user_id or not user_id.isdigit() or not len(user_id) == 9 or len(password) < PASSWORD_LENGTH:
        return incorrect_credentials

    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (int(user_id),)
    ).fetchone()

    if user is None or not check_password_hash(user['password'], password):
        return incorrect_credentials

    session.clear()
    user = dict(user)
    user['is_student'] = bool(user['is_student'])
    session['user'] = user
    return {}, 200


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return {}, 200


@bp.route('/change-password', methods=['PUT'])
@login_required
def change_password():
    try:
        new_password = request.form['password']
    except KeyError:
        return INCORRECT_VALUES

    if len(new_password) < PASSWORD_LENGTH:
        return {"error": "הסיסמה חייבת להיות בת 6 תווים לפחות"}, 400

    if check_password_hash(session['user']['password'], new_password):
        return {"error": "הסיסמה חייבת להיות שונה מהסיסמה הקודמת"}, 403

    db = get_db()
    new_password_hash = generate_password_hash(new_password)
    db.execute(
        "UPDATE user SET password = ? WHERE id == ?",
        (new_password_hash, session['user']['id']),
    )
    db.commit()

    session['user']['password'] = new_password_hash
    session.modified = True

    return {}, 200
