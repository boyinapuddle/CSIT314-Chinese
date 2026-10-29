"""UC05 - Find matching fields within the designer's own company."""
from flask import Blueprint, render_template, request
from app.company_support import designer_required, own_company

search_company_bp = Blueprint("search_company", __name__)


@search_company_bp.get("/company/search")
@designer_required
def search():
    company = own_company()
    query = request.args.get("q", "").strip()
    matches = []
    error = None
    if len(query) > 200:
        error = "Search must be 200 characters or fewer."
    elif company and query:
        for field, label in (("name", "Company name"), ("description", "Description"),
                             ("email", "Email"), ("phone", "Phone"), ("address", "Address")):
            value = getattr(company, field)
            if value and query.casefold() in value.casefold():
                matches.append((label, value))
    return render_template("company/search.html", company=company, query=query, matches=matches, error=error), (422 if error else 200)
