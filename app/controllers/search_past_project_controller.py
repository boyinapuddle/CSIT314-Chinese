"""UC17 - Search titles and descriptions within the designer's past projects."""
from flask import Blueprint, render_template, request

from app.company_support import designer_required, own_company
from app.entities import Project
from app.extensions import db
from app.project_support import owned_projects

search_past_project_bp = Blueprint("search_past_project", __name__)


@search_past_project_bp.get("/projects/past/search")
@designer_required
def search():
    query = request.args.get("q", "").strip()
    error = "Search must be 200 characters or fewer." if len(query) > 200 else None
    projects = []
    if query and not error:
        projects = db.session.scalars(owned_projects("past").where(db.or_(
            Project.title.icontains(query, autoescape=True),
            Project.description.icontains(query, autoescape=True),
        )).order_by(Project.created_at.desc(), Project.id.desc())).all()
    return render_template("projects/past/list.html", company=own_company(), projects=projects,
                           searching=True, query=query, error=error), (422 if error else 200)
