from flask import (
    Blueprint, session, request
)

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('checks', __name__, url_prefix='/checks')
