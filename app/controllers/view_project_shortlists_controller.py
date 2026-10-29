"""UC19 - View unique shortlist counts for the designer's projects."""
from flask import Blueprint, render_template

from app.analytics_support import project_counts
from app.company_support import designer_required
from app.entities import Shortlist

view_project_shortlists_bp = Blueprint("view_project_shortlists", __name__)


@view_project_shortlists_bp.get("/analytics/shortlists")
@view_project_shortlists_bp.get("/projects/<int:project_id>/analytics/shortlists")
@designer_required
def view(project_id=None):
    return render_template("analytics/counts.html", rows=project_counts(Shortlist, project_id), metric="shortlists")
