"""UC08 - Create a current interior design project."""
from flask import Blueprint, flash, redirect, render_template, url_for

from app.company_support import designer_required, own_company
from app.entities import Project
from app.extensions import db
from app.project_support import ProjectForm

create_current_project_bp = Blueprint("create_current_project", __name__)


@create_current_project_bp.route("/projects/current/create", methods=["GET", "POST"])
@designer_required
def create():
    company = own_company()
    if company is None:
        flash("Create your company before adding projects.", "error")
        return redirect(url_for("create_company.create"))
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(company_id=company.id, status="current")
        form.apply_to(project)
        db.session.add(project)
        db.session.commit()
        flash("Current project created.", "success")
        return redirect(url_for("view_current_project.detail", project_id=project.id))
    return render_template("projects/current/form.html", form=form, editing=False), (422 if form.is_submitted() else 200)
