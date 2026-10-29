"""UC02 - View the designer's own company."""
from flask import Blueprint, redirect, render_template, url_for
from app.company_support import designer_required, own_company, require_owned_company

view_company_bp = Blueprint("view_company", __name__)


@view_company_bp.get("/company")
@designer_required
def index():
    company = own_company()
    if company:
        return redirect(url_for("view_company.detail", company_id=company.id))
    return render_template("company/detail.html", company=None)


@view_company_bp.get("/companies/<int:company_id>")
@designer_required
def detail(company_id):
    return render_template("company/detail.html", company=require_owned_company(company_id))
