from flask import Blueprint

bp = Blueprint('main', __name__)

import stations.main.routes