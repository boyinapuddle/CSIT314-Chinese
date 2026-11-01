import os

from flask import Flask

from .database import get_db, init_app
from .seed_data import seed_database


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me"),
        DATABASE=os.environ.get(
            "DATABASE",
            os.path.join(app.instance_path, "platform.sqlite"),
        ),
    )

    if test_config:
        app.config.update(test_config)

    init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    if not app.config.get("TESTING") and os.environ.get("AUTO_SEED", "1") == "1":
        with app.app_context():
            seed_database(get_db(), reset=False)

    return app
