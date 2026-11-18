
import re
import secrets
import hashlib
from datetime import datetime, timedelta

import mysql.connector

from flask import Blueprint, request, jsonify
from flask_mail import Message

from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from database import get_db_connection
from extensions import mail


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# Validate email address
def is_valid_email(email):
    return bool(
        re.fullmatch(
            r'[^@\s]+@[^@\s]+\.[^@\s]+',
            email
        )
    )


# User Registration API
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "status": "Error",
            "message": "Invalid JSON data"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "status": "Error",
            "message": "Name, email and password are required"
        }), 400

    if not all(isinstance(value, str) for value in [name, email, password]):
        return jsonify({
            "status": "Error",
            "message": "All fields must be text"
        }), 400

    name = name.strip()
    email = email.strip().lower()

    if not name or len(name) > 100:
        return jsonify({
            "status": "Error",
            "message": "Name must be between 1 and 100 characters"
        }), 400

    if len(email) > 150 or not is_valid_email(email):
        return jsonify({
            "status": "Error",
            "message": "Please provide a valid email address"
        }), 400

    if len(password) < 8:
        return jsonify({
            "status": "Error",
            "message": "Password must contain at least 8 characters"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "status": "Error",
                "message": "Database connection failed"
            }), 500

        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return jsonify({
                "status": "Error",
                "message": "Email is already registered"
            }), 409

        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
        )

        connection.commit()

        user_id = cursor.lastrowid

        return jsonify({
            "status": "Success",
            "message": "Registration successful",
            "user": {
                "user_id": user_id,
                "name": name,
                "email": email
            }
        }), 201

    except mysql.connector.IntegrityError:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "Error",
            "message": "Email is already registered"
        }), 409

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "Error",
            "message": "Database operation failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# User Login API
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "status": "Error",
            "message": "Invalid JSON data"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "status": "Error",
            "message": "Email and password are required"
        }), 400

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "status": "Error",
            "message": "Email and password must be text"
        }), 400

    email = email.strip().lower()

    if len(email) > 150 or not is_valid_email(email):
        return jsonify({
            "status": "Error",
            "message": "Please provide a valid email address"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "status": "Error",
                "message": "Database connection failed"
            }), 500

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, name, email, password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user or not check_password_hash(
            user["password"],
            password
        ):
            return jsonify({
                "status": "Error",
                "message": "Invalid email or password"
            }), 401

        access_token = create_access_token(
            identity=str(user["user_id"])
        )

        return jsonify({
            "status": "Success",
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200

    except mysql.connector.Error:
        return jsonify({
            "status": "Error",
            "message": "Database operation failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# JWT Protected User Profile API
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "status": "Error",
                "message": "Database connection failed"
            }), 500

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, name, email, created_at
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status": "Error",
                "message": "User not found"
            }), 404

        return jsonify({
            "status": "Success",
            "message": "Profile retrieved successfully",
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "created_at": str(user["created_at"])
            }
        }), 200

    except mysql.connector.Error:
        return jsonify({
            "status": "Error",
            "message": "Database operation failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# User Logout API
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    token_data = get_jwt()
    token_id = token_data["jti"]

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "status": "Error",
                "message": "Database connection failed"
            }), 500

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO token_blocklist (jti)
            VALUES (%s)
            """,
            (token_id,)
        )

        connection.commit()

        return jsonify({
            "status": "Success",
            "message": "Logout successful"
        }), 200

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "Error",
            "message": "Logout failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# Forgot Password API
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "status": "Error",
            "message": "Invalid JSON data"
        }), 400

    email = data.get("email")

    if not isinstance(email, str) or not email.strip():
        return jsonify({
            "status": "Error",
            "message": "Email is required"
        }), 400

    email = email.strip().lower()

    if len(email) > 150 or not is_valid_email(email):
        return jsonify({
            "status": "Error",
            "message": "Please provide a valid email address"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "status": "Error",
                "message": "Database connection failed"
            }), 500

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, name, email
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        # Generic response prevents email enumeration
        if not user:
            return jsonify({
                "status": "Success",
                "message": "If an account exists with this email, a reset token will be sent."
            }), 200

        # Generate a secure random token
        reset_token = secrets.token_urlsafe(32)

        # Store only the SHA-256 hash
        token_hash = hashlib.sha256(
            reset_token.encode("utf-8")
        ).hexdigest()

        expires_at = datetime.utcnow() + timedelta(minutes=15)

        # Invalidate previous unused reset tokens
        cursor.execute(
            """
            DELETE FROM password_reset_tokens
            WHERE user_id = %s AND used_at IS NULL
            """,
            (user["user_id"],)
        )

        cursor.execute(
            """
            INSERT INTO password_reset_tokens
            (user_id, token_hash, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user["user_id"], token_hash, expires_at)
        )

        connection.commit()

        # Send reset token through email
        message = Message(
            subject="F-commerce Growth AI - Password Reset",
            recipients=[user["email"]]
        )

        message.body = f"""
Hello {user['name']},

We received a request to reset your F-commerce Growth AI account password.

Your password reset token is:

{reset_token}

This token expires in 15 minutes and can only be used once.

To reset your password, send a POST request to:

http://127.0.0.1:5000/api/auth/reset-password

Request JSON:
{{
    "token": "YOUR_RESET_TOKEN",
    "new_password": "YOUR_NEW_PASSWORD"
}}

If you did not request a password reset, you can ignore this email.

Regards,
F-commerce Growth AI Team
"""

        mail.send(message)

        return jsonify({
            "status": "Success",
            "message": "If an account exists with this email, a reset token will be sent."
        }), 200

    except Exception:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "Error",
            "message": "Unable to process password reset request. Please try again later."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# Reset Password API
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "status": "Error",
            "message": "Invalid JSON data"
        }), 400

    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({
            "status": "Error",
            "message": "Reset token and new password are required"
        }), 400

    if not isinstance(token, str) or not isinstance(new_password, str):
        return jsonify({
            "status": "Error",
            "message": "Token and password must be text"
        }), 400

    if len(new_password) < 8:
        return jsonify({
            "status": "Error",
            "message": "Password must contain at least 8 characters"
        }), 400

    # Hash the received token
    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "status": "Error",
                "message": "Database connection failed"
            }), 500

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT reset_id, user_id
            FROM password_reset_tokens
            WHERE token_hash = %s
              AND used_at IS NULL
              AND expires_at > UTC_TIMESTAMP()
            """,
            (token_hash,)
        )

        reset_record = cursor.fetchone()

        if not reset_record:
            return jsonify({
                "status": "Error",
                "message": "Invalid, expired or already used reset token"
            }), 400

        hashed_password = generate_password_hash(new_password)

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE user_id = %s
            """,
            (hashed_password, reset_record["user_id"])
        )

        cursor.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = UTC_TIMESTAMP()
            WHERE reset_id = %s AND used_at IS NULL
            """,
            (reset_record["reset_id"],)
        )

        connection.commit()

        return jsonify({
            "status": "Success",
            "message": "Password reset successful. You can now log in with your new password."
        }), 200

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "Error",
            "message": "Password reset failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
