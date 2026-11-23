
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models.sales_order import SalesOrder
from app.models.customer import Customer
from app.services.order_service import (
    create_draft_order,
    confirm_order,
    cancel_order
)

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


def order_to_dict(order):
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_id": order.customer_id,
        "customer_name": order.customer.customer_name if order.customer else None,
        "user_id": order.user_id,
        "order_date": order.order_date.isoformat() if order.order_date else None,
        "status": order.status,
        "discount_percent": float(order.discount_percent),
        "subtotal": float(order.subtotal),
        "discount_amount": float(order.discount_amount),
        "grand_total": float(order.grand_total),
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.product_name if item.product else None,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "line_total": float(item.line_total)
            }
            for item in order.items
        ]
    }


def can_access_order(order):
    return current_user.role == "Admin" or order.user_id == current_user.id


# GET ALL ORDERS
@orders_bp.route("/", methods=["GET"])
@login_required
def get_orders():
    if current_user.role == "Admin":
        orders = SalesOrder.query.order_by(
            SalesOrder.order_date.desc()
        ).all()
    else:
        orders = SalesOrder.query.filter_by(
            user_id=current_user.id
        ).order_by(SalesOrder.order_date.desc()).all()

    return jsonify([order_to_dict(order) for order in orders]), 200


# CREATE DRAFT ORDER
@orders_bp.route("/", methods=["POST"])
@login_required
def create_order():
    data = request.get_json(silent=True) or {}

    try:
        order = create_draft_order(
            customer_id=data.get("customer_id"),
            user_id=current_user.id,
            items=data.get("items", []),
            discount_percent=data.get("discount_percent", 0)
        )

        return jsonify({
            "message": "Draft order created successfully",
            "order": order_to_dict(order)
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Unable to create order"}), 500


# GET SINGLE ORDER
@orders_bp.route("/<int:order_id>", methods=["GET"])
@login_required
def get_order(order_id):
    order = db.session.get(SalesOrder, order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if not can_access_order(order):
        return jsonify({"error": "Access denied"}), 403

    return jsonify(order_to_dict(order)), 200


# CONFIRM ORDER
@orders_bp.route("/<int:order_id>/confirm", methods=["POST"])
@login_required
def confirm_sales_order(order_id):
    order = db.session.get(SalesOrder, order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if not can_access_order(order):
        return jsonify({"error": "Access denied"}), 403

    try:
        confirmed_order = confirm_order(order_id, current_user.id)

        return jsonify({
            "message": "Order confirmed successfully",
            "order": order_to_dict(confirmed_order)
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Unable to confirm order"}), 500


# CANCEL ORDER
@orders_bp.route("/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel_sales_order(order_id):
    order = db.session.get(SalesOrder, order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if not can_access_order(order):
        return jsonify({"error": "Access denied"}), 403

    try:
        cancelled_order = cancel_order(order_id, current_user.id)

        return jsonify({
            "message": "Order cancelled successfully",
            "order": order_to_dict(cancelled_order)
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Unable to cancel order"}), 500
