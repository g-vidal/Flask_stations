from flask import Blueprint

bp = Blueprint('omutils', __name__)

import stations.omutils.routes
