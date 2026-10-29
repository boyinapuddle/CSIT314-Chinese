import os
import click
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, url_for
from flask_login import current_user, login_required
from werkzeug.exceptions import HTTPException
from app.extensions import csrf, db, login_manager

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY in .env")
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("Set DATABASE_URL in .env")
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"

    from app.entities import User  # load all entities before create_all
    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    from app.controllers.create_company_controller import create_company_bp
    from app.controllers.view_company_controller import view_company_bp
    from app.controllers.update_company_controller import update_company_bp
    from app.controllers.delete_company_controller import delete_company_bp
    from app.controllers.search_company_controller import search_company_bp
    for blueprint in (create_company_bp, view_company_bp, update_company_bp, delete_company_bp, search_company_bp):
        app.register_blueprint(blueprint)

    from app.controllers.create_current_project_controller import create_current_project_bp
    from app.controllers.view_current_project_controller import view_current_project_bp
    from app.controllers.update_current_project_controller import update_current_project_bp
    from app.controllers.delete_current_project_controller import delete_current_project_bp
    from app.controllers.search_current_project_controller import search_current_project_bp
    for blueprint in (create_current_project_bp, view_current_project_bp, update_current_project_bp,
                      delete_current_project_bp, search_current_project_bp):
        app.register_blueprint(blueprint)

    from app.controllers.create_past_project_controller import create_past_project_bp
    from app.controllers.view_past_project_controller import view_past_project_bp
    from app.controllers.update_past_project_controller import update_past_project_bp
    from app.controllers.delete_past_project_controller import delete_past_project_bp
    from app.controllers.search_past_project_controller import search_past_project_bp
    for blueprint in (create_past_project_bp, view_past_project_bp, update_past_project_bp,
                      delete_past_project_bp, search_past_project_bp):
        app.register_blueprint(blueprint)

    from app.controllers.view_project_views_controller import view_project_views_bp
    from app.controllers.view_project_shortlists_controller import view_project_shortlists_bp
    from app.public_projects import public_projects_bp
    for blueprint in (view_project_views_bp, view_project_shortlists_bp, public_projects_bp):
        app.register_blueprint(blueprint)

    @app.errorhandler(HTTPException)
    def http_error(error):
        messages = {
            400: ("Please reload the form", "Your form may have expired or could not be processed. Reload the page and submit it again."),
            403: ("This action is unavailable", "Your account does not have access to this action."),
            404: ("We couldn't find that page", "The page may have been removed, or it may belong to another designer."),
            405: ("This request is unavailable", "Open the page and use its links or form to continue."),
        }
        heading, message = messages.get(error.code, (error.name, "Return to your workspace and try again."))
        response = error.get_response()
        response.set_data(render_template("error.html", error=error, heading=heading, message=message))
        response.content_type = "text/html; charset=utf-8"
        return response

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id)) if user_id.isdigit() else None

    @app.route("/")
    def home():
        return redirect(url_for("main.dashboard" if current_user.is_authenticated else "auth.login"))

    from flask import Blueprint
    main_bp = Blueprint("main", __name__)

    @main_bp.get("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    app.register_blueprint(main_bp)

    @app.cli.command("init-db")
    def init_db():
        """Development only: create missing PostgreSQL tables."""
        db.create_all()
        click.echo("Database tables created (if missing).")

    @app.cli.command("create-designer")
    @click.option("--email", prompt=True)
    @click.password_option()
    def create_designer(email, password):
        """Provision a login without implementing an unrequested registration story."""
        from app.entities import User
        email = email.strip().lower()
        if db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none():
            raise click.ClickException("Email already exists")
        if len(password) < 12:
            raise click.ClickException("Password must be at least 12 characters")
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo("Interior Designer account created.")

    from app.demo import register_demo_command
    register_demo_command(app)

    return app
