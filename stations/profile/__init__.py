from flask import Blueprint

bp = Blueprint('profile', __name__)

import stations.profile.routes