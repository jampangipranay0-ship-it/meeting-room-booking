from flask import Blueprint, redirect, render_template, request, session, url_for, flash

from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = auth_service.authenticate(email, password)
        if user:
            flash("Login successful", "success")
            if user.get("role") == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("employee.dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    auth_service.logout()
    flash("Logged out", "info")
    return redirect(url_for("main.home"))
