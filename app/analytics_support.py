"""Shared owner-scoped count queries for the two analytics stories."""
from flask import abort
from flask_login import current_user

from app.entities import Company, Project
from app.extensions import db


def project_counts(metric, project_id=None):
    count = db.select(db.func.count()).select_from(metric).where(
        metric.project_id == Project.id
    ).correlate(Project).scalar_subquery()
    query = db.select(Project, count.label("count")).join(Company).where(
        Company.owner_id == current_user.id
    ).order_by(Project.created_at.desc(), Project.id.desc())
    if project_id is not None:
        query = query.where(Project.id == project_id)
    rows = db.session.execute(query).all()
    if project_id is not None and not rows:
        abort(404)
    return rows
