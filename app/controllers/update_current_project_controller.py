"""UC10 - Edit a current project's text fields."""
from flask import Blueprint, flash, redirect, render_template, url_for

from app.company_support import designer_required
from app.extensions import db
from app.project_support import ProjectForm, require_owned_project

update_current_project_bp = Blueprint("update_current_project", __name__)


@update_current_project_bp.route("/projects/current/<int:project_id>/edit", methods=["GET", "POST"])
@designer_required
def update(project_id):
    project = require_owned_project(project_id, "current")
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        form.apply_to(project)
        db.session.commit()
        flash("Current project updated.", "success")
        return redirect(url_for("view_current_project.detail", project_id=project.id))
    return render_template("projects/current/form.html", form=form, project=project, editing=True), (422 if form.is_submitted() else 200)
