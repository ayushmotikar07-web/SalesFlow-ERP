
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")


def admin_required():
    return current_user.is_authenticated and current_user.role == "Admin"


@inventory_bp.route("/adjustments", methods=["POST"])
@login_required
def adjust_stock():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}

    try:
        product_id = int(data.get("product_id"))
        adjustment = int(data.get("quantity_change"))
        reason = str(data.get("reason", "")).strip()

        if adjustment == 0:
            return jsonify({"error": "Quantity change cannot be zero"}), 400

        if not reason:
            return jsonify({"error": "A reason is required"}), 400

        product = Product.query.filter_by(id=product_id).with_for_update().first()

        if not product:
            return jsonify({"error": "Product not found"}), 404

        new_stock = product.stock_quantity + adjustment

        if new_stock < 0:
            return jsonify({
                "error": "Insufficient stock for this adjustment",
                "current_stock": product.stock_quantity
            }), 400

        product.stock_quantity = new_stock

        movement = StockMovement(
            product_id=product.id,
            movement_type="ADJUSTMENT",
            quantity_change=adjustment,
            reference_type="Manual Adjustment",
            reference_id=None,
            reason=reason,
            user_id=current_user.id
        )

        db.session.add(movement)
        db.session.commit()

        return jsonify({
            "message": "Stock adjusted successfully",
            "product_id": product.id,
            "product_name": product.product_name,
            "quantity_change": adjustment,
            "new_stock": product.stock_quantity
        }), 200

    except (TypeError, ValueError):
        db.session.rollback()
        return jsonify({
            "error": "product_id and quantity_change must be valid integers"
        }), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Unable to adjust stock"}), 500


@inventory_bp.route("/movements", methods=["GET"])
@login_required
def get_stock_movements():
    query = StockMovement.query.order_by(StockMovement.created_at.desc())

    product_id = request.args.get("product_id")
    movement_type = request.args.get("movement_type")

    if product_id:
        try:
            query = query.filter_by(product_id=int(product_id))
        except ValueError:
            return jsonify({"error": "Invalid product_id"}), 400

    if movement_type:
        query = query.filter_by(movement_type=movement_type.strip())

    movements = query.limit(500).all()

    return jsonify([
        {
            "id": movement.id,
            "product_id": movement.product_id,
            "product_name": movement.product.product_name if movement.product else None,
            "movement_type": movement.movement_type,
            "quantity_change": movement.quantity_change,
            "reference_type": movement.reference_type,
            "reference_id": movement.reference_id,
            "reason": movement.reason,
            "user_id": movement.user_id,
            "created_at": movement.created_at.isoformat() if movement.created_at else None
        }
        for movement in movements
    ]), 200
