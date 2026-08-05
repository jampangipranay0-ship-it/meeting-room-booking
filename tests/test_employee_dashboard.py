import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app


def test_employee_dashboard_renders_after_login():
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()

    response = client.post(
        "/login",
        data={"email": "employee@multirecruit.com", "password": "employee123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"My Bookings" in response.data
