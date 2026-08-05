import csv
import io
from datetime import datetime

from flask import Response
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ReportService:
    @staticmethod
    def export_csv(bookings):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "date", "room_name", "booked_by", "employee_id", "purpose", "client_name", "start_time", "end_time", "duration_hours", "status"])
        writer.writeheader()
        writer.writerows(bookings)
        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=bookings.csv"})

    @staticmethod
    def export_excel(bookings):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Bookings"
        headers = ["id", "date", "room_name", "booked_by", "employee_id", "purpose", "client_name", "start_time", "end_time", "duration_hours", "status"]
        sheet.append(headers)
        for booking in bookings:
            sheet.append([booking.get(field, "") for field in headers])
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)
        return Response(output.getvalue(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=bookings.xlsx"})

    @staticmethod
    def export_pdf(bookings):
        output = io.BytesIO()
        pdf = canvas.Canvas(output, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(40, 760, "Meeting Room Booking Report")
        y = 730
        for booking in bookings[:20]:
            pdf.drawString(40, y, f"{booking.get('date')} | {booking.get('room_name')} | {booking.get('booked_by')} | {booking.get('status')}")
            y -= 15
        pdf.save()
        output.seek(0)
        return Response(output.getvalue(), mimetype="application/pdf", headers={"Content-Disposition": "attachment; filename=bookings.pdf"})
