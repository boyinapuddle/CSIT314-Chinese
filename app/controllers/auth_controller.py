"""UC06 and UC07: one controller for log in and log out."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from app.entities import User
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("You have logged out.", "success")
    return redirect(url_for("auth.login"))
