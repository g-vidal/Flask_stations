from flask import Blueprint

bp = Blueprint('explore', __name__)

import orientation.explore.routes
