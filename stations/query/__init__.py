from flask import Blueprint

bp = Blueprint('query', __name__)

import orientation.query.routes