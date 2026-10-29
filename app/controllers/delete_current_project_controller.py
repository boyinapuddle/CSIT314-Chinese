"""UC11 - Confirm and delete a current project and its dependent analytics."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.company_support import designer_required
from app.entities import ProjectView, Shortlist
from app.extensions import db
from app.project_support import require_owned_project

delete_current_project_bp = Blueprint("delete_current_project", __name__)


@delete_current_project_bp.route("/projects/current/<int:project_id>/delete", methods=["GET", "POST"])
@designer_required
def delete(project_id):
    project = require_owned_project(project_id, "current")
    if request.method == "POST" and request.form.get("confirmation") == "delete":
        db.session.delete(project)
        db.session.commit()
        flash("Current project deleted.", "success")
        return redirect(url_for("view_current_project.index"))
    counts = {
        "views": db.session.scalar(db.select(db.func.count()).select_from(ProjectView).filter_by(project_id=project.id)),
        "shortlists": db.session.scalar(db.select(db.func.count()).select_from(Shortlist).filter_by(project_id=project.id)),
    }
    if request.method == "POST":
        flash("Confirm that you want to delete this project and its analytics.", "error")
    return render_template("projects/current/delete.html", project=project, counts=counts), (422 if request.method == "POST" else 200)
