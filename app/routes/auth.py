
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    print("\n--- LOGIN DEBUG ---")
    print("Received username:", repr(username))

    if not username or not password:
        print("Username or password is empty")
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    print("User found:", user is not None)

    if user is None:
        return jsonify({"error": "User not found"}), 401

    password_correct = user.check_password(password)
    print("Password correct:", password_correct)
    print("Account active:", user.is_active)

    if not password_correct:
        return jsonify({"error": "Incorrect password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is inactive"}), 403

    login_user(user)

    print("LOGIN SUCCESSFUL")
    print("------------------\n")

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def current_user_info():
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }), 200
