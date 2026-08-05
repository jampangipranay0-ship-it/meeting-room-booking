from flask import Flask, jsonify

from routes.auth import auth_bp
from routes.main import main_bp
from routes.employee import employee_bp
from routes.admin import admin_bp
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(employee_bp, url_prefix="/employee")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "meeting-room-booking"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
