"""Shared company forms and ownership checks; story routes live in controllers."""
from functools import wraps
import re

from flask import abort
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from app.entities import Company
from app.extensions import db


def validate_email(form, field):
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", field.data):
        raise ValidationError("Enter a valid email address.")


def trimmed(value):
    return value.strip() if isinstance(value, str) else value


class CompanyForm(FlaskForm):
    name = StringField("Company name", filters=[trimmed], validators=[InputRequired(), Length(max=200)])
    description = TextAreaField("Description", filters=[trimmed], validators=[Optional(), Length(max=10000)])
    email = StringField("Email", filters=[trimmed], validators=[Optional(), Length(max=254), validate_email])
    phone = StringField("Phone", filters=[trimmed], validators=[Optional(), Length(max=40)])
    address = TextAreaField("Address", filters=[trimmed], validators=[Optional(), Length(max=500)])

    def validate_name(self, field):
        if not field.data:
            raise ValidationError("Company name is required.")

    def apply_to(self, company):
        for name in ("name", "description", "email", "phone", "address"):
            setattr(company, name, getattr(self, name).data or None)


def designer_required(handler):
    @wraps(handler)
    @login_required
    def checked(*args, **kwargs):
        if current_user.role != "interior_designer":
            abort(403)
        return handler(*args, **kwargs)
    return checked


def own_company():
    return db.session.execute(db.select(Company).filter_by(owner_id=current_user.id)).scalar_one_or_none()


def require_owned_company(company_id):
    company = db.session.execute(
        db.select(Company).filter_by(id=company_id, owner_id=current_user.id)
    ).scalar_one_or_none()
    if company is None:
        abort(404)
    return company
