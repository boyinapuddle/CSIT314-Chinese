"""UC03 - Update company information."""
from flask import Blueprint, flash, redirect, render_template, url_for
from app.company_support import CompanyForm, designer_required, require_owned_company
from app.extensions import db

update_company_bp = Blueprint("update_company", __name__)


@update_company_bp.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
@designer_required
def update(company_id):
    company = require_owned_company(company_id)
    form = CompanyForm(obj=company)
    if form.validate_on_submit():
        form.apply_to(company)
        db.session.commit()
        flash("Company updated.", "success")
        return redirect(url_for("view_company.detail", company_id=company.id))
    return render_template("company/form.html", form=form, editing=True, company=company), (422 if form.is_submitted() else 200)
