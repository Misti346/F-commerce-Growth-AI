
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from database import get_db_connection
from extensions import mail

from routes.orders import orders_bp
from routes.customers import customers_bp
from routes.products import products_bp
from routes.ai import ai_bp
from routes.auth import auth_bp


app = Flask(__name__)


# CORS Configuration - Allow localhost on any port
CORS(app, resources={
    r"/api/*": {
        "origins": r"http://(localhost|127\.0\.0\.1)(:\d+)?$"
    }
})


# Gmail SMTP Configuration
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_USERNAME")
)

mail.init_app(app)


# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_BLACKLIST_ENABLED"] = True

if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("JWT_SECRET_KEY is missing from backend/.env")

jwt = JWTManager(app)


# Check whether JWT token has been revoked
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        if connection is None:
            return True

        cursor = connection.cursor()

        cursor.execute(
            "SELECT jti FROM token_blocklist WHERE jti = %s",
            (jwt_payload["jti"],)
        )

        return cursor.fetchone() is not None

    except Exception as e:
        print("Token blocklist check failed:", e)
        return True

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# Register API blueprints
app.register_blueprint(orders_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(products_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(auth_bp)


@app.route("/")
def home():
    return jsonify({
        "message": "F-commerce Growth AI Backend is Running!",
        "status": "Success"
    })


@app.route("/test-db")
def test_database():
    connection = get_db_connection()

    if connection:
        connection.close()
        return jsonify({
            "message": "MySQL Database Connected Successfully!",
            "status": "Success"
        })

    return jsonify({
        "message": "Database Connection Failed!",
        "status": "Error"
    }), 500


if __name__ == "__main__":
    app.run(debug=True)
