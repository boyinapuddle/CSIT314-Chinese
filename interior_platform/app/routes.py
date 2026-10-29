from functools import wraps
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for
from .boundaries import *
from .entities import UserSession


bp = Blueprint("main", __name__)


def role_required(*roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            account_id = session.get("account_id")
            session_id = session.get("session_id")
            if not account_id or not session_id or not UserSession.is_active(session_id):
                session.clear()
                return redirect(url_for("main.login"))
            if roles and session.get("role") not in roles:
                abort(403)
            return function(*args, **kwargs)
        return wrapper
    return decorator


LOGOUT_BOUNDARIES = {
    "User Admin": UserAdminLogoutBoundary,
    "Interior Designer": InteriorDesignerLogoutBoundary,
    "Customer": CustomerLogoutBoundary,
    "Platform Manager": PlatformManagerLogoutBoundary,
}


REPORT_BOUNDARIES = {
    "daily": GenerateDailyReportBoundary,
    "weekly": GenerateWeeklyReportBoundary,
    "monthly": GenerateMonthlyReportBoundary,
}


@bp.route("/")
def home():
    projects = []
    if session.get("role") == "Customer":
        projects = SearchAvailableIDPBoundary().submit("")[:6]
    return render_template("home.html", projects=projects)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        result = LoginBoundary().submit(request.form)
        if result:
            account, session_id = result
            session.update(
                account_id=account["account_id"],
                role=account["role"],
                display_name=account["display_name"],
                session_id=session_id,
            )
            return redirect(url_for("main.dashboard"))
        flash("Login failed. Check credentials and account profile status.", "error")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session_context = dict(session)
    role = session_context.get("role")
    boundary_class = LOGOUT_BOUNDARIES.get(role)
    if boundary_class:
        boundary_class().submit(session_context)
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/dashboard")
@role_required()
def dashboard():
    return render_template("dashboard.html")


@bp.route("/admin/profiles", methods=["GET", "POST"])
@role_required("User Admin")
def admin_profiles():
    if request.method == "POST":
        CreateUserProfileBoundary().submit(request.form)
        flash("Profile created.", "success")
    keyword = request.args.get("q", "")
    items = SearchUserProfileBoundary().submit(keyword)
    return render_template("admin_profiles.html", items=items)


@bp.route("/admin/profiles/<int:profile_id>")
@role_required("User Admin")
def view_profile(profile_id):
    row = ViewUserProfileBoundary().request(profile_id)
    if not row:
        abort(404)
    return jsonify(dict(row))


@bp.route("/admin/profiles/<int:profile_id>/edit", methods=["POST"])
@role_required("User Admin")
def edit_profile(profile_id):
    UpdateUserProfileBoundary().submit(profile_id, request.form)
    return redirect(url_for("main.admin_profiles"))


@bp.route("/admin/profiles/<int:profile_id>/suspend", methods=["POST"])
@role_required("User Admin")
def suspend_profile(profile_id):
    SuspendUserProfileBoundary().submit(profile_id)
    return redirect(url_for("main.admin_profiles"))


@bp.route("/admin/accounts", methods=["GET", "POST"])
@role_required("User Admin")
def admin_accounts():
    create_boundary = CreateUserAccountBoundary()
    if request.method == "POST":
        create_boundary.submit(request.form)
        flash("Account created.", "success")
    keyword = request.args.get("q", "")
    items = SearchUserAccountBoundary().submit(keyword)
    return render_template(
        "admin_accounts.html",
        items=items,
        profiles=create_boundary.profiles(),
    )


@bp.route("/admin/accounts/<int:account_id>")
@role_required("User Admin")
def view_account(account_id):
    row = ViewUserAccountBoundary().request(account_id)
    if not row:
        abort(404)
    return jsonify(dict(row))


@bp.route("/admin/accounts/<int:account_id>/edit", methods=["POST"])
@role_required("User Admin")
def edit_account(account_id):
    UpdateUserAccountBoundary().submit(account_id, request.form)
    return redirect(url_for("main.admin_accounts"))


@bp.route("/admin/accounts/<int:account_id>/suspend", methods=["POST"])
@role_required("User Admin")
def suspend_account(account_id):
    SuspendUserAccountBoundary().submit(account_id)
    return redirect(url_for("main.admin_accounts"))


@bp.route("/designer/company", methods=["GET", "POST"])
@role_required("Interior Designer")
def designer_company():
    session_context = dict(session)
    view_boundary = ViewCompanyInformationBoundary()
    company = view_boundary.request(session_context)
    if request.method == "POST":
        if company:
            UpdateCompanyInformationBoundary().submit(session_context, request.form)
            flash("Company information updated.", "success")
        else:
            CreateCompanyInformationBoundary().submit(session_context, request.form)
            flash("Company information created.", "success")
        company = view_boundary.request(session_context)
    keyword = request.args.get("q", "").strip()
    matches = []
    if keyword:
        matches = SearchCompanyInformationBoundary().submit(session_context, keyword)
    return render_template(
        "company.html",
        company=company,
        matches=matches,
        q=keyword,
    )


@bp.route("/designer/company/delete", methods=["POST"])
@role_required("Interior Designer")
def delete_company():
    DeleteCompanyInformationBoundary().submit(dict(session))
    flash("Company information deleted.", "success")
    return redirect(url_for("main.designer_company"))


@bp.route("/designer/projects/<status>", methods=["GET", "POST"])
@role_required("Interior Designer")
def designer_projects(status):
    project_status = "Current" if status.lower() == "current" else "Past"
    session_context = dict(session)
    keyword = request.args.get("q", "")
    if project_status == "Current":
        create_boundary = CreateCurrentIDPBoundary()
        if request.method == "POST":
            create_boundary.submit(session_context, request.form)
            flash("Current project created.", "success")
        if keyword:
            items = SearchCurrentIDPBoundary().submit(session_context, keyword)
        else:
            items = ViewCurrentIDPBoundary().request(session_context)
    else:
        create_boundary = CreatePastIDPBoundary()
        if request.method == "POST":
            create_boundary.submit(session_context, request.form)
            flash("Past project created.", "success")
        if keyword:
            items = SearchPastIDPBoundary().submit(session_context, keyword)
        else:
            items = ViewPastIDPBoundary().request(session_context)
    return render_template(
        "designer_projects.html",
        status=project_status,
        items=items,
        categories=create_boundary.categories(),
    )


@bp.route("/designer/projects/<status>/<int:project_id>/edit", methods=["POST"])
@role_required("Interior Designer")
def edit_project(status, project_id):
    session_context = dict(session)
    if status.lower() == "past":
        UpdatePastIDPBoundary().submit(session_context, project_id, request.form)
    else:
        UpdateCurrentIDPBoundary().submit(session_context, project_id, request.form)
    flash("Project updated.", "success")
    return redirect(request.referrer or url_for("main.dashboard"))


@bp.route("/designer/projects/<status>/<int:project_id>/delete", methods=["POST"])
@role_required("Interior Designer")
def delete_project(status, project_id):
    session_context = dict(session)
    if status.lower() == "past":
        DeletePastIDPBoundary().submit(session_context, project_id)
    else:
        DeleteCurrentIDPBoundary().submit(session_context, project_id)
    flash("Project deleted.", "success")
    return redirect(request.referrer or url_for("main.dashboard"))


@bp.route("/projects")
@role_required("Customer")
def projects():
    keyword = request.args.get("q", "")
    items = SearchAvailableIDPBoundary().submit(keyword)
    return render_template("projects.html", items=items)


@bp.route("/projects/<int:project_id>")
@role_required("Customer")
def project_detail(project_id):
    project = ViewAvailableIDPBoundary().request(dict(session), project_id)
    if not project:
        abort(404)
    return render_template("project_detail.html", p=project)


@bp.route("/projects/<int:project_id>/save", methods=["POST"])
@role_required("Customer")
def save_project(project_id):
    added = SaveIDPBoundary().submit(dict(session), project_id)
    if added:
        flash("Project saved.", "success")
    else:
        flash("Project already saved or unavailable.", "error")
    return redirect(request.referrer or url_for("main.projects"))


@bp.route("/favourites")
@role_required("Customer")
def favourites():
    keyword = request.args.get("q", "")
    if keyword:
        items = SearchSavedIDPBoundary().submit(dict(session), keyword)
    else:
        items = ViewSavedIDPBoundary().request(dict(session))
    return render_template("favourites.html", items=items)


@bp.route("/designer/analytics")
@role_required("Interior Designer")
def analytics():
    session_context = dict(session)
    view_rows = ViewIDPViewsBoundary().request(session_context)
    shortlist_rows = ViewIDPShortlistsBoundary().request(session_context)
    return render_template(
        "analytics.html",
        items=view_rows,
        shortlist_items=shortlist_rows,
    )


@bp.route("/manager/categories", methods=["GET", "POST"])
@role_required("Platform Manager")
def categories():
    if request.method == "POST":
        try:
            CreateIDPCategoryBoundary().submit(request.form)
            flash("Category created.", "success")
        except Exception:
            flash("Category already exists or data is invalid.", "error")
    keyword = request.args.get("q", "")
    if keyword:
        items = SearchIDPCategoryBoundary().submit(keyword)
    else:
        items = ViewIDPCategoryBoundary().request_all()
    return render_template("categories.html", items=items)


@bp.route("/manager/categories/<int:category_id>")
@role_required("Platform Manager")
def view_category(category_id):
    row = ViewIDPCategoryBoundary().request(category_id)
    if not row:
        abort(404)
    return jsonify(dict(row))


@bp.route("/manager/categories/<int:category_id>/edit", methods=["POST"])
@role_required("Platform Manager")
def edit_category(category_id):
    UpdateIDPCategoryBoundary().submit(category_id, request.form)
    return redirect(url_for("main.categories"))


@bp.route("/manager/categories/<int:category_id>/suspend", methods=["POST"])
@role_required("Platform Manager")
def suspend_category(category_id):
    SuspendIDPCategoryBoundary().submit(category_id)
    return redirect(url_for("main.categories"))


@bp.route("/manager/reports/<period>")
@role_required("Platform Manager")
def reports(period):
    boundary_class = REPORT_BOUNDARIES.get(period)
    if not boundary_class:
        abort(404)
    report = boundary_class().submit(request.args.get("date"))
    return render_template("reports.html", report=report)
