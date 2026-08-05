from flask import Blueprint, redirect, render_template, request, session, url_for, flash, Response

from services.booking_service import BookingService
from services.auth_service import AuthService
from services.report_service import ReportService

admin_bp = Blueprint("admin", __name__)
booking_service = BookingService()
auth_service = AuthService()
report_service = ReportService()


@admin_bp.before_request
def require_admin():
    user = auth_service.current_user()
    if not user:
        return redirect(url_for("auth.login"))
    if user.get("role") != "admin":
        return redirect(url_for("auth.login"))


@admin_bp.route("/dashboard")
def dashboard():
    stats = booking_service.get_dashboard_stats()
    bookings = booking_service.get_all_bookings()
    return render_template("admin_dashboard.html", stats=stats, bookings=bookings)


@admin_bp.route("/bookings/<booking_id>/edit", methods=["GET", "POST"])
def edit_booking(booking_id):
    booking = booking_service.booking_repo.get_by_id(booking_id)
    if not booking:
        flash("Booking not found", "danger")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            booking_service.update_booking(booking_id, form_data)
            flash("Booking updated successfully", "success")
            return redirect(url_for("admin.dashboard"))
        except ValueError as exc:
            flash(str(exc), "danger")
            booking.update(form_data)

    rooms = room_repo.get_all()
    return render_template("admin_edit_booking.html", booking=booking, rooms=rooms)


@admin_bp.route("/bookings/<booking_id>/approve", methods=["POST"])
def approve_booking(booking_id):
    booking = booking_service.booking_repo.get_by_id(booking_id)
    if booking:
        booking["status"] = "Booked"
        booking["approved_by"] = auth_service.current_user().get("name")
        booking_service.update_booking(booking_id, booking)
        flash("Booking approved", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/bookings/<booking_id>/reject", methods=["POST"])
def reject_booking(booking_id):
    booking = booking_service.booking_repo.get_by_id(booking_id)
    if booking:
        booking["status"] = "Rejected"
        booking_service.update_booking(booking_id, booking)
        flash("Booking rejected", "danger")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/reports/csv")
def export_csv():
    return report_service.export_csv(booking_service.get_all_bookings())


@admin_bp.route("/reports/excel")
def export_excel():
    return report_service.export_excel(booking_service.get_all_bookings())


@admin_bp.route("/reports/pdf")
def export_pdf():
    return report_service.export_pdf(booking_service.get_all_bookings())
