"""UC18 - View counts for the designer's current and past projects."""
from flask import Blueprint, render_template

from app.analytics_support import project_counts
from app.company_support import designer_required
from app.entities import ProjectView

view_project_views_bp = Blueprint("view_project_views", __name__)


@view_project_views_bp.get("/analytics/views")
@view_project_views_bp.get("/projects/<int:project_id>/analytics/views")
@designer_required
def view(project_id=None):
    return render_template("analytics/counts.html", rows=project_counts(ProjectView, project_id), metric="views")
