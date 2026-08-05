from flask import Blueprint, redirect, render_template, request, session, url_for, flash

from services.booking_service import BookingService
from services.auth_service import AuthService

employee_bp = Blueprint("employee", __name__)
booking_service = BookingService()
auth_service = AuthService()


@employee_bp.before_request
def require_login():
    user = auth_service.current_user()
    if not user:
        return redirect(url_for("auth.login"))
    if user.get("role") != "employee":
        return redirect(url_for("auth.login"))


@employee_bp.route("/dashboard")
def dashboard():
    user = auth_service.current_user()
    bookings = booking_service.get_employee_bookings(user.get("id"))
    upcoming = booking_service.get_upcoming(user.get("id"))
    return render_template("employee_dashboard.html", bookings=bookings, upcoming=upcoming, user=user)


@employee_bp.route("/booking/<booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    booking = booking_service.get_all_bookings()
    for item in booking:
        if item.get("id") == booking_id:
            item["status"] = "Cancelled"
            booking_service.update_booking(booking_id, item)
            flash("Booking cancelled", "success")
            break
    return redirect(url_for("employee.dashboard"))
