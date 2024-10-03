from flask import Blueprint

bp = Blueprint('omvideos', __name__)
import stations.omvideos.routes
