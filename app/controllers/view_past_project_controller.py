"""UC14 - View only the designer's past projects."""
from flask import Blueprint, render_template

from app.company_support import designer_required, own_company
from app.entities import Project
from app.extensions import db
from app.project_support import owned_projects, require_owned_project

view_past_project_bp = Blueprint("view_past_project", __name__)


@view_past_project_bp.get("/projects/past")
@designer_required
def index():
    projects = db.session.scalars(
        owned_projects("past").order_by(Project.created_at.desc(), Project.id.desc())
    ).all()
    return render_template("projects/past/list.html", projects=projects, company=own_company(), searching=False)


@view_past_project_bp.get("/projects/past/<int:project_id>")
@designer_required
def detail(project_id):
    return render_template("projects/past/detail.html", project=require_owned_project(project_id, "past"))
