"""Minimal public engagement infrastructure supporting UC18 and UC19.

Direct links only: no customer accounts or public browsing directory.
"""
import secrets
from time import time

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.entities import Project, ProjectView, Shortlist
from app.extensions import db

public_projects_bp = Blueprint("public_projects", __name__)
VIEW_INTERVAL = 30 * 60
MAX_RECENT_PROJECTS = 100


def is_owner(project):
    return current_user.is_authenticated and project.company.owner_id == current_user.id


def visitor_token():
    if "visitor_token" not in session:
        session["visitor_token"] = secrets.token_hex(32)
    return session["visitor_token"]


def find_shortlist(project_id, token):
    return db.session.scalar(db.select(Shortlist).filter_by(project_id=project_id, visitor_token=token))


@public_projects_bp.after_request
def prevent_caching(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@public_projects_bp.get("/portfolio/projects/<int:project_id>")
def detail(project_id):
    project = db.get_or_404(Project, project_id)
    owner = is_owner(project)
    # HEAD, private designer pages and the owner's public preview never count.
    if request.method == "GET" and not owner:
        now = time()
        recent = {key: stamp for key, stamp in session.get("recent_project_views", {}).items()
                  if now - stamp < VIEW_INTERVAL}
        key = str(project.id)
        if key not in recent:
            db.session.add(ProjectView(project_id=project.id))
            db.session.commit()
            recent[key] = now
        recent = dict(sorted(recent.items(), key=lambda item: item[1])[-MAX_RECENT_PROJECTS:])
        session["recent_project_views"] = recent
    shortlisted = False
    if not owner and request.method == "GET":
        shortlisted = find_shortlist(project.id, visitor_token()) is not None
    return render_template("public/project.html", project=project, owner=owner, shortlisted=shortlisted)


@public_projects_bp.post("/portfolio/projects/<int:project_id>/shortlist")
def shortlist(project_id):
    project = db.get_or_404(Project, project_id)
    if is_owner(project):
        abort(403)
    token = visitor_token()
    if find_shortlist(project.id, token) is None:
        db.session.add(Shortlist(project_id=project.id, visitor_token=token))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # The unique constraint also handles simultaneous repeat submissions.
            if find_shortlist(project_id, token) is None:
                raise
    flash("Project shortlisted for this browser.", "success")
    return redirect(url_for("public_projects.detail", project_id=project_id))
