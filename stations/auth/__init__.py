from flask import Blueprint

bp = Blueprint('auth', __name__)

import orientation.auth.routes