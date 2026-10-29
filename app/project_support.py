"""Reusable project forms and queries; routes remain in story controllers."""
from flask import abort
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from app.company_support import trimmed
from app.entities import Company, Project
from app.extensions import db


class ProjectForm(FlaskForm):
    title = StringField("Project title", filters=[trimmed], validators=[InputRequired(), Length(max=200)])
    description = TextAreaField("Description", filters=[trimmed], validators=[Optional(), Length(max=10000)])

    def validate_title(self, field):
        if not field.data:
            raise ValidationError("Project title is required.")

    def apply_to(self, project):
        project.title = self.title.data
        project.description = self.description.data or None


def owned_projects(status):
    return db.select(Project).join(Company).where(
        Company.owner_id == current_user.id, Project.status == status,
    )


def require_owned_project(project_id, status):
    project = db.session.scalar(owned_projects(status).where(Project.id == project_id))
    if project is None:
        abort(404)
    return project
