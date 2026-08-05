# Multi Recruit Meeting Room Booking

A modern internal meeting room booking system built with Flask, Bootstrap 5, and JSON-backed storage with a repository pattern for future migration to SQLite/MySQL/Google Sheets.

## Features

- Role-based login for employees and admins
- Room discovery with dynamic room cards
- Booking form with validation and conflict detection
- Extension requests for bookings over 2 hours
- Admin dashboard for approvals, editing, deleting, and reporting
- Employee dashboard with upcoming and historical bookings
- CSV, Excel, and PDF export
- Responsive, modern UI with dark mode support

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000.

## Default credentials

- Admin: admin@multirecruit.com / admin123
- Employee: employee@multirecruit.com / employee123
