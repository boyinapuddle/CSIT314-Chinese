from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, jsonify
from .controllers import *
from .repositories import ProfileRepository
from .services import CategoryService

bp = Blueprint('main', __name__)


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if not session.get('account_id'):
                return redirect(url_for('main.login'))
            if roles and session.get('role') not in roles:
                abort(403)
            return fn(*a, **kw)
        return wrapper
    return deco


LOGIN_CONTROLLERS = (
    UserAdminLoginController,
    InteriorDesignerLoginController,
    CustomerLoginController,
    PlatformManagerLoginController,
)
LOGOUT_CONTROLLERS = {
    'User Admin': UserAdminLogoutController,
    'Interior Designer': InteriorDesignerLogoutController,
    'Customer': CustomerLogoutController,
    'Platform Manager': PlatformManagerLogoutController,
}


@bp.route('/')
def home():
    projects = SearchAvailableIDPController().search('')[:6] if session.get('role') == 'Customer' else []
    return render_template('home.html', projects=projects)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = None
        # Each role has its own story-specific login controller (US11/18/35/47).
        for controller_cls in LOGIN_CONTROLLERS:
            result = controller_cls().login(request.form['username'], request.form['password'])
            if result:
                break
        if result:
            account, sid = result
            session.update(
                account_id=account['account_id'], role=account['role'],
                display_name=account['display_name'], session_id=sid,
            )
            return redirect(url_for('main.dashboard'))
        flash('Login failed. Check credentials and account/profile status.', 'error')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    role = session.get('role')
    sid = session.get('session_id')
    if sid and role in LOGOUT_CONTROLLERS:
        LOGOUT_CONTROLLERS[role]().logout(sid)
    session.clear()
    return redirect(url_for('main.login'))


@bp.route('/dashboard')
@role_required()
def dashboard():
    return render_template('dashboard.html')



# US01-US10 - User Admin profiles and accounts

@bp.route('/admin/profiles', methods=['GET', 'POST'])
@role_required('User Admin')
def admin_profiles():
    if request.method == 'POST':
        CreateUserProfileController().create(request.form['name'], request.form.get('description', ''))
        flash('Profile created.', 'success')
    items = SearchUserProfileController().search(request.args.get('q', ''))
    return render_template('admin_profiles.html', items=items)


@bp.route('/admin/profiles/<int:pid>')
@role_required('User Admin')
def view_profile(pid):
    row = ViewUserProfileController().view(pid)
    if not row: abort(404)
    return jsonify(dict(row))


@bp.route('/admin/profiles/<int:pid>/edit', methods=['POST'])
@role_required('User Admin')
def edit_profile(pid):
    UpdateUserProfileController().update(pid, request.form['name'], request.form.get('description', ''))
    return redirect(url_for('main.admin_profiles'))


@bp.route('/admin/profiles/<int:pid>/suspend', methods=['POST'])
@role_required('User Admin')
def suspend_profile(pid):
    SuspendUserProfileController().suspend(pid)
    return redirect(url_for('main.admin_profiles'))


@bp.route('/admin/accounts', methods=['GET', 'POST'])
@role_required('User Admin')
def admin_accounts():
    if request.method == 'POST':
        CreateUserAccountController().create(
            request.form['username'], request.form['password'], int(request.form['profile_id']),
            request.form['display_name'], request.form['email'],
        )
        flash('Account created.', 'success')
    items = SearchUserAccountController().search(request.args.get('q', ''))
    return render_template('admin_accounts.html', items=items, profiles=ProfileRepository().search(''))


@bp.route('/admin/accounts/<int:aid>')
@role_required('User Admin')
def view_account(aid):
    row = ViewUserAccountController().view(aid)
    if not row: abort(404)
    return jsonify(dict(row))


@bp.route('/admin/accounts/<int:aid>/edit', methods=['POST'])
@role_required('User Admin')
def edit_account(aid):
    UpdateUserAccountController().update(
        aid, request.form['display_name'], request.form['email'], int(request.form['profile_id'])
    )
    return redirect(url_for('main.admin_accounts'))


@bp.route('/admin/accounts/<int:aid>/suspend', methods=['POST'])
@role_required('User Admin')
def suspend_account(aid):
    SuspendUserAccountController().suspend(aid)
    return redirect(url_for('main.admin_accounts'))



# US13-US17 - Interior Designer company information

@bp.route('/designer/company', methods=['GET', 'POST'])
@role_required('Interior Designer')
def designer_company():
    did = session['account_id']
    viewer = ViewCompanyInformationController()
    if request.method == 'POST':
        if viewer.view(did):
            UpdateCompanyInformationController().update(did, request.form)
            flash('Company information updated.', 'success')
        else:
            CreateCompanyInformationController().create(did, request.form)
            flash('Company information created.', 'success')
    q = request.args.get('q', '').strip()
    matches = SearchCompanyInformationController().search(did, q) if q else []
    return render_template('company.html', company=viewer.view(did), matches=matches, q=q)


@bp.route('/designer/company/delete', methods=['POST'])
@role_required('Interior Designer')
def delete_company():
    DeleteCompanyInformationController().delete(session['account_id'])
    flash('Company information deleted.', 'success')
    return redirect(url_for('main.designer_company'))



# US20-US29 - Interior Designer current/past IDP portfolio

@bp.route('/designer/projects/<status>', methods=['GET', 'POST'])
@role_required('Interior Designer')
def designer_projects(status):
    status = 'Current' if status.lower() == 'current' else 'Past'
    did = session['account_id']
    q = request.args.get('q', '')

    if request.method == 'POST':
        if status == 'Current':
            CreateCurrentIDPController().create(did, request.form)
        else:
            CreatePastIDPController().create(did, request.form)
        flash(f'{status} project created.', 'success')

    if status == 'Current':
        items = (SearchCurrentIDPController().search(did, q) if q
                 else ViewCurrentIDPController().view(did))
    else:
        items = (SearchPastIDPController().search(did, q) if q
                 else ViewPastIDPController().view(did))

    return render_template(
        'designer_projects.html', status=status, items=items,
        categories=CategoryService().search('', True),
    )


@bp.route('/designer/projects/<int:pid>/edit', methods=['POST'])
@role_required('Interior Designer')
def edit_project(pid):
    status = request.form.get('project_status', 'Current').title()
    if status == 'Past':
        UpdatePastIDPController().update(pid, session['account_id'], request.form)
    else:
        UpdateCurrentIDPController().update(pid, session['account_id'], request.form)
    flash('Project updated.', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))


@bp.route('/designer/projects/<status>/<int:pid>/delete', methods=['POST'])
@role_required('Interior Designer')
def delete_project(status, pid):
    if status.lower() == 'past':
        DeletePastIDPController().delete(pid, session['account_id'])
    else:
        DeleteCurrentIDPController().delete(pid, session['account_id'])
    flash('Project deleted.', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))



# US30-US34 - Customer explore/save favourites

@bp.route('/projects')
@role_required('Customer')
def projects():
    return render_template('projects.html', items=SearchAvailableIDPController().search(request.args.get('q', '')))


@bp.route('/projects/<int:pid>')
@role_required('Customer')
def project_detail(pid):
    p = ViewAvailableIDPController().view(pid, session['account_id'])
    if not p: abort(404)
    return render_template('project_detail.html', p=p)


@bp.route('/projects/<int:pid>/save', methods=['POST'])
@role_required('Customer')
def save_project(pid):
    added = SaveIDPController().save(session['account_id'], pid)
    flash('Project saved.' if added else 'Project already saved or unavailable.', 'success' if added else 'error')
    return redirect(request.referrer or url_for('main.projects'))


@bp.route('/favourites')
@role_required('Customer')
def favourites():
    q = request.args.get('q', '')
    if q:
        items = SearchSavedIDPController().search(session['account_id'], q)
    else:
        items = ViewSavedIDPController().view(session['account_id'])
    return render_template('favourites.html', items=items)



# US37-US38 - Designer project interest metrics

@bp.route('/designer/analytics')
@role_required('Interior Designer')
def analytics():
    did = session['account_id']
    view_rows = ViewIDPViewsController().view(did)
    shortlist_rows = ViewIDPShortlistsController().view(did)
    # Both use cases are executed independently; the template can display both
    # counts because each project row contains views and shortlists.
    return render_template('analytics.html', items=view_rows, shortlist_items=shortlist_rows)



# US39-US43 - Platform Manager IDP categories

@bp.route('/manager/categories', methods=['GET', 'POST'])
@role_required('Platform Manager')
def categories():
    if request.method == 'POST':
        try:
            CreateIDPCategoryController().create(request.form['name'], request.form.get('description', ''))
            flash('Category created.', 'success')
        except Exception:
            flash('Category already exists or data is invalid.', 'error')
    q = request.args.get('q', '')
    items = SearchIDPCategoryController().search(q) if q else ViewIDPCategoryController().view_all()
    return render_template('categories.html', items=items)


@bp.route('/manager/categories/<int:cid>')
@role_required('Platform Manager')
def view_category(cid):
    row = ViewIDPCategoryController().view(cid)
    if not row: abort(404)
    return jsonify(dict(row))


@bp.route('/manager/categories/<int:cid>/edit', methods=['POST'])
@role_required('Platform Manager')
def edit_category(cid):
    UpdateIDPCategoryController().update(cid, request.form['name'], request.form.get('description', ''))
    return redirect(url_for('main.categories'))


@bp.route('/manager/categories/<int:cid>/suspend', methods=['POST'])
@role_required('Platform Manager')
def suspend_category(cid):
    SuspendIDPCategoryController().suspend(cid)
    return redirect(url_for('main.categories'))



# US44-US46 - Platform Manager reports

REPORT_CONTROLLERS = {
    'daily': GenerateDailyReportController,
    'weekly': GenerateWeeklyReportController,
    'monthly': GenerateMonthlyReportController,
}


@bp.route('/manager/reports/<period>')
@role_required('Platform Manager')
def reports(period):
    controller_cls = REPORT_CONTROLLERS.get(period)
    if not controller_cls: abort(404)
    report = controller_cls().generate(request.args.get('date'))
    return render_template('reports.html', report=report)
