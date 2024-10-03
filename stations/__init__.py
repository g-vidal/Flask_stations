from flask import Flask
from config import Config
from stations.extensions import db
from stations.extensions import cache
from werkzeug.middleware.proxy_fix import ProxyFix

from stations.main import dbtools

def create_app(config_class=Config):

    # Create Flask app load app.config
    app = Flask(__name__, instance_relative_config=True)
    
    # modify proxy to serve on subtree
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    app.config.from_object(config_class)

    # Initialize Flask extensions here (initialize database)
    db.init_app(app)
    cache.init_app(app)

    # Register blueprints here
    from stations.main import bp as main_bp
    app.register_blueprint(main_bp)
    from stations.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from stations.profile import bp as profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')
    from stations.explore import bp as explore_bp
    app.register_blueprint(explore_bp, url_prefix='/explore')
    from stations.omutils import bp as utils_bp
    app.register_blueprint(utils_bp, url_prefix='/omutils')
    from stations.query import bp as query_bp
    app.register_blueprint(query_bp, url_prefix='/query')
    from stations.omvideos import bp as videos_bp
    app.register_blueprint(videos_bp, url_prefix='/omvideos')

    # create database stations.db
    dbtools.construct_db(app)

    # test route
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
