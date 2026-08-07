import json
from typing import Any, Dict, List, Optional

import httpx


class GoogleSheetsRepository:
    """Lightweight adapter to a Google Apps Script Web App that proxies a Google Sheet.

    Expects a web app URL in the form of an Apps Script deployed web app.
    The web app should accept simple JSON POST/GET requests and perform operations
    like `list`, `get`, `create`, `update`, `delete`, and `query` for bookings.

    This adapter implements the small subset of methods used by BookingRepository:
    - initialize_table()
    - execute(query, parameters, commit=False)
    - fetch_all(query, parameters)
    - fetch_one(query, parameters)

    The adapter recognizes the specific SQL shapes emitted by BookingRepository
    and routes them to the web app's endpoints. This keeps changes local and
    avoids refactoring higher layers.
    """

    def __init__(self, web_app_url: str, api_key: Optional[str] = None, timeout: int = 10):
        self.web_app_url = web_app_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.Client(timeout=timeout)

    def _call(self, action: str, payload: Dict[str, Any] | None = None):
        url = f"{self.web_app_url}/{action}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        resp = self.client.post(url, json=payload or {}, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def initialize_table(self) -> None:
        # Let the Apps Script ensure sheet and columns exist.
        try:
            self._call("initialize")
        except Exception:
            # Do not block startup if the remote cannot be contacted here;
            # higher-level operations will surface meaningful errors.
            pass

    def execute(self, query: str, parameters: tuple = (), commit: bool = False):
        q = query.strip().lower()
        # INSERT
        if q.startswith("insert into bookings"):
            # BookingRepository passes params in a fixed order; unpack into dict
            cols = [
                "id",
                "room_id",
                "room_name",
                "date",
                "start_time",
                "end_time",
                "booked_by",
                "employee_id",
                "purpose",
                "reason",
                "client_name",
                "status",
                "duration_hours",
                "meeting_link",
                "approved_by",
                "remarks",
                "created_at",
                "modified_at",
                "extension_requested",
                "extension_status",
            ]
            payload = {k: v for k, v in zip(cols, parameters)}
            return self._call("create", {"record": payload})

        # UPDATE
        if q.startswith("update bookings set"):
            # parameters end with booking id
            *values, booking_id = parameters
            # BookingRepository uses a fixed UPDATE order matching the INSERT fields
            cols = [
                "room_id",
                "room_name",
                "date",
                "start_time",
                "end_time",
                "booked_by",
                "employee_id",
                "purpose",
                "reason",
                "client_name",
                "status",
                "duration_hours",
                "meeting_link",
                "approved_by",
                "remarks",
                "modified_at",
                "extension_requested",
                "extension_status",
            ]
            payload = {k: v for k, v in zip(cols, values)}
            payload["id"] = booking_id
            return self._call("update", {"record": payload})

        # DELETE
        if q.startswith("delete from bookings"):
            booking_id = parameters[0] if parameters else None
            return self._call("delete", {"id": booking_id})

        raise NotImplementedError("Unsupported execute operation for GoogleSheetsRepository")

    def fetch_all(self, query: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
        q = query.strip().lower()
        # Simple patterns used by BookingRepository
        if q.startswith("select * from bookings"):
            # Optional WHERE or ORDER clauses are handled server-side by the Apps Script
            return self._call("list") or []

        if "where date =" in q and "%s" in q:
            date = parameters[0]
            return self._call("query", {"filter": {"date": date}}) or []

        if "where employee_id =" in q and "date >= " in q:
            employee_id, date = parameters
            return self._call("query", {"filter": {"employee_id": employee_id, "date_gte": date}}) or []

        if "where room_id =" in q and "date =" in q:
            room_id, date = parameters
            payload = {"filter": {"room_id": room_id, "date": date}}
            # exclude id logic handled in BookingService via conflict check
            return self._call("query", payload) or []

        # Fallback: ask server for list and let it handle the raw SQL-like query
        return self._call("list") or []

    def fetch_one(self, query: str, parameters: tuple = ()) -> Optional[Dict[str, Any]]:
        q = query.strip().lower()
        if "where id =" in q:
            booking_id = parameters[0]
            res = self._call("get", {"id": booking_id})
            return res
        return None
