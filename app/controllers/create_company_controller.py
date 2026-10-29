"""UC01 - Create company information."""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.company_support import CompanyForm, designer_required, own_company
from app.entities import Company
from app.extensions import db

create_company_bp = Blueprint("create_company", __name__)


@create_company_bp.route("/company/create", methods=["GET", "POST"])
@designer_required
def create():
    company = own_company()
    if company:
        flash("You already have a company. You can edit its information.", "error")
        return redirect(url_for("view_company.detail", company_id=company.id))
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(owner_id=current_user.id)
        form.apply_to(company)
        db.session.add(company)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            company = own_company()
            if company is None:
                raise
            flash("You already have a company.", "error")
            return redirect(url_for("view_company.detail", company_id=company.id))
        flash("Company created.", "success")
        return redirect(url_for("view_company.detail", company_id=company.id))
    return render_template("company/form.html", form=form, editing=False), (422 if form.is_submitted() else 200)
