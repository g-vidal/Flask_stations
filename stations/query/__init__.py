from flask import Blueprint

bp = Blueprint('query', __name__)

import stations.query.routes