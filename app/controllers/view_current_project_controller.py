"""UC09 - View only the designer's current projects."""
from flask import Blueprint, render_template

from app.company_support import designer_required, own_company
from app.entities import Project
from app.extensions import db
from app.project_support import owned_projects, require_owned_project

view_current_project_bp = Blueprint("view_current_project", __name__)


@view_current_project_bp.get("/projects/current")
@designer_required
def index():
    projects = db.session.scalars(
        owned_projects("current").order_by(Project.created_at.desc(), Project.id.desc())
    ).all()
    return render_template("projects/current/list.html", projects=projects, company=own_company(), searching=False)


@view_current_project_bp.get("/projects/current/<int:project_id>")
@designer_required
def detail(project_id):
    return render_template("projects/current/detail.html", project=require_owned_project(project_id, "current"))
