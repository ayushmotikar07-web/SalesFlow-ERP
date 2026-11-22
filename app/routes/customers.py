
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps

from app import db
from app.models import Customer

customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/api/customers"
)


# Allow only Admin users to modify customer records
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != "Admin":
            return jsonify({"error": "Admin access required"}), 403

        return func(*args, **kwargs)

    return wrapper


# Convert customer object into JSON
def customer_to_dict(customer):
    return {
        "id": customer.id,
        "customer_name": customer.customer_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "is_active": customer.is_active
    }


# GET all customers
@customers_bp.route("/", methods=["GET"])
@login_required
def get_customers():
    customers = Customer.query.all()

    if current_user.role != "Admin":
        customers = Customer.query.filter_by(is_active=True).all()

    return jsonify([
        customer_to_dict(customer)
        for customer in customers
    ]), 200


# GET one customer
@customers_bp.route("/<int:customer_id>", methods=["GET"])
@login_required
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    if current_user.role != "Admin" and not customer.is_active:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer_to_dict(customer)), 200


# ADD a new customer
@customers_bp.route("/", methods=["POST"])
@login_required
@admin_required
def add_customer():
    data = request.get_json(silent=True) or {}

    customer_name = data.get("customer_name", "").strip()

    if not customer_name:
        return jsonify({"error": "Customer name is required"}), 400

    customer = Customer(
        customer_name=customer_name,
        email=data.get("email"),
        phone=data.get("phone"),
        address=data.get("address"),
        is_active=True
    )

    try:
        db.session.add(customer)
        db.session.commit()

        return jsonify({
            "message": "Customer created successfully",
            "customer": customer_to_dict(customer)
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not create customer"}), 400


# UPDATE a customer
@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@login_required
@admin_required
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    data = request.get_json(silent=True) or {}

    allowed_fields = ["customer_name", "email", "phone", "address"]

    for field in allowed_fields:
        if field in data:
            value = data[field]

            if field == "customer_name":
                value = value.strip() if isinstance(value, str) else ""

                if not value:
                    return jsonify({
                        "error": "Customer name cannot be empty"
                    }), 400

            setattr(customer, field, value)

    try:
        db.session.commit()

        return jsonify({
            "message": "Customer updated successfully",
            "customer": customer_to_dict(customer)
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not update customer"}), 400


# DEACTIVATE a customer instead of deleting
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@login_required
@admin_required
def deactivate_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    customer.is_active = False

    try:
        db.session.commit()

        return jsonify({
            "message": "Customer deactivated successfully"
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not deactivate customer"}), 400
