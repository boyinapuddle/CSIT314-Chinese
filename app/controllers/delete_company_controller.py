"""UC04 - Confirm and delete company information without cascading project loss."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.company_support import designer_required, require_owned_company
from app.entities import Project
from app.extensions import db

delete_company_bp = Blueprint("delete_company", __name__)


@delete_company_bp.route("/companies/<int:company_id>/delete", methods=["GET", "POST"])
@designer_required
def delete(company_id):
    company = require_owned_company(company_id)
    # Lock the parent on PostgreSQL so a concurrent project insert cannot slip
    # between checking dependencies and deleting the company.
    if request.method == "POST":
        db.session.execute(db.select(type(company)).filter_by(id=company.id).with_for_update()).scalar_one()
    project_count = db.session.scalar(
        db.select(db.func.count()).select_from(Project).filter_by(company_id=company.id)
    )
    if request.method == "POST":
        if project_count:
            flash("Delete the company's projects first. Their views and shortlists must not be removed accidentally.", "error")
            return render_template("company/delete.html", company=company, project_count=project_count), 409
        if request.form.get("confirmation") != "delete":
            flash("Confirm that you want to delete this company.", "error")
            return render_template("company/delete.html", company=company, project_count=0), 422
        db.session.delete(company)
        db.session.commit()
        flash("Company deleted.", "success")
        return redirect(url_for("view_company.index"))
    return render_template("company/delete.html", company=company, project_count=project_count)
