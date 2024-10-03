from flask import Blueprint

bp = Blueprint('omutils', __name__)

import orientation.omutils.routes
