"""UC13 - Create a past interior design project."""
from flask import Blueprint, flash, redirect, render_template, url_for

from app.company_support import designer_required, own_company
from app.entities import Project
from app.extensions import db
from app.project_support import ProjectForm

create_past_project_bp = Blueprint("create_past_project", __name__)


@create_past_project_bp.route("/projects/past/create", methods=["GET", "POST"])
@designer_required
def create():
    company = own_company()
    if company is None:
        flash("Create your company before adding projects.", "error")
        return redirect(url_for("create_company.create"))
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(company_id=company.id, status="past")
        form.apply_to(project)
        db.session.add(project)
        db.session.commit()
        flash("Past project created.", "success")
        return redirect(url_for("view_past_project.detail", project_id=project.id))
    return render_template("projects/past/form.html", form=form, editing=False), (422 if form.is_submitted() else 200)
