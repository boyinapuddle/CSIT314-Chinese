"""UC15 - Edit a past project's text fields."""
from flask import Blueprint, flash, redirect, render_template, url_for

from app.company_support import designer_required
from app.extensions import db
from app.project_support import ProjectForm, require_owned_project

update_past_project_bp = Blueprint("update_past_project", __name__)


@update_past_project_bp.route("/projects/past/<int:project_id>/edit", methods=["GET", "POST"])
@designer_required
def update(project_id):
    project = require_owned_project(project_id, "past")
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        form.apply_to(project)
        db.session.commit()
        flash("Past project updated.", "success")
        return redirect(url_for("view_past_project.detail", project_id=project.id))
    return render_template("projects/past/form.html", form=form, project=project, editing=True), (422 if form.is_submitted() else 200)
