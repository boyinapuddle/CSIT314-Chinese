import os
from flask import Flask
from .database import init_app

def create_app(test_config=None):
    app=Flask(__name__)
    app.config.from_mapping(SECRET_KEY=os.environ.get('SECRET_KEY','dev-change-me'), DATABASE=os.environ.get('DATABASE',os.path.join(app.instance_path,'platform.sqlite')))
    if test_config: app.config.update(test_config)
    init_app(app)
    from .routes import bp
    app.register_blueprint(bp)
    return app
