from flask import Blueprint

bp = Blueprint('omvideos', __name__)
import orientation.omvideos.routes
