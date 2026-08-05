from flask import Blueprint, redirect, render_template, request, url_for, flash, jsonify

from services.booking_service import BookingService
from services.auth_service import AuthService
from repositories.json_repository import JsonRepository
from repositories.room_repository import RoomRepository
from config import Config

main_bp = Blueprint("main", __name__)
booking_service = BookingService()
auth_service = AuthService()
room_repo = RoomRepository(JsonRepository(Config.ROOMS_PATH))


@main_bp.route("/")
def home():
    rooms = room_repo.get_all()
    bookings = booking_service.get_upcoming_bookings()
    return render_template("home.html", rooms=rooms, bookings=bookings)


@main_bp.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            booking = booking_service.create_booking(form_data)
            flash("Booking submitted successfully", "success")
            return render_template("booking_confirmation.html", booking=booking)
        except ValueError as exc:
            flash(str(exc), "danger")
    rooms = room_repo.get_all()
    return render_template("book.html", rooms=rooms)


@main_bp.route("/goodbye")
def goodbye():
    return render_template("goodbye.html")


@main_bp.route("/room_availability")
def room_availability():
    room_id = request.args.get("room_id")
    date = request.args.get("date")
    if not room_id or not date:
        return jsonify([])

    bookings = booking_service.get_bookings_for_room_date(room_id, date)
    return jsonify([
        {
            "start_time": booking["start_time"],
            "end_time": booking["end_time"],
            "purpose": booking.get("purpose", ""),
            "client_name": booking.get("client_name", ""),
            "status": booking.get("status", "Booked"),
        }
        for booking in bookings
    ])
