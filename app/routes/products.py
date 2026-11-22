
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from decimal import Decimal, InvalidOperation
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Product

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products"
)


# Only Admin users can modify products
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != "Admin":
            return jsonify({"error": "Admin access required"}), 403
        return func(*args, **kwargs)
    return wrapper


# Convert product object into JSON
def product_to_dict(product):
    return {
        "id": product.id,
        "product_code": product.product_code,
        "product_name": product.product_name,
        "category": product.category,
        "price": str(product.price),
        "stock_quantity": product.stock_quantity,
        "status": product.status
    }


# Validate price and stock
def validate_product_data(data):
    try:
        price = Decimal(str(data.get("price", "")))
        stock = int(data.get("stock_quantity", ""))
    except (InvalidOperation, ValueError, TypeError):
        return None, None, "Enter a valid price and stock quantity"

    if not price.is_finite() or price < 0:
        return None, None, "Price cannot be negative"

    if stock < 0:
        return None, None, "Stock quantity cannot be negative"

    if isinstance(data.get("stock_quantity"), bool):
        return None, None, "Stock quantity must be a whole number"

    if price.as_tuple().exponent < -2:
        return None, None, "Price can have at most two decimal places"

    return price, stock, None


# GET all products
@products_bp.route("/", methods=["GET"])
@login_required
def get_products():
    query = Product.query

    if current_user.role != "Admin":
        query = query.filter_by(status="Active")

    search = request.args.get("search", "").strip()

    if search:
        query = query.filter(
            db.or_(
                Product.product_name.ilike(f"%{search}%"),
                Product.product_code.ilike(f"%{search}%"),
                Product.category.ilike(f"%{search}%")
            )
        )

    products = query.order_by(Product.id.desc()).all()

    return jsonify([
        product_to_dict(product)
        for product in products
    ]), 200


# GET one product
@products_bp.route("/<int:product_id>", methods=["GET"])
@login_required
def get_product(product_id):
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    if current_user.role != "Admin" and product.status != "Active":
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product_to_dict(product)), 200


# ADD a product
@products_bp.route("/", methods=["POST"])
@login_required
@admin_required
def add_product():
    data = request.get_json(silent=True) or {}

    product_code = data.get("product_code")
    product_name = data.get("product_name")

    if not isinstance(product_code, str) or not product_code.strip():
        return jsonify({"error": "Product code is required"}), 400

    if not isinstance(product_name, str) or not product_name.strip():
        return jsonify({"error": "Product name is required"}), 400

    price, stock, error = validate_product_data(data)

    if error:
        return jsonify({"error": error}), 400

    product = Product(
        product_code=product_code.strip(),
        product_name=product_name.strip(),
        category=data.get("category"),
        price=price,
        stock_quantity=stock,
        status="Active"
    )

    try:
        db.session.add(product)
        db.session.commit()

        return jsonify({
            "message": "Product created successfully",
            "product": product_to_dict(product)
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Product code already exists"}), 409

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not create product"}), 400


# UPDATE a product
@products_bp.route("/<int:product_id>", methods=["PUT"])
@login_required
@admin_required
def update_product(product_id):
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json(silent=True) or {}

    if "product_code" in data:
        if not isinstance(data["product_code"], str) or not data["product_code"].strip():
            return jsonify({"error": "Product code cannot be empty"}), 400
        product.product_code = data["product_code"].strip()

    if "product_name" in data:
        if not isinstance(data["product_name"], str) or not data["product_name"].strip():
            return jsonify({"error": "Product name cannot be empty"}), 400
        product.product_name = data["product_name"].strip()

    if "category" in data:
        product.category = data["category"]

    if "price" in data or "stock_quantity" in data:
        values = {
            "price": data.get("price", product.price),
            "stock_quantity": data.get("stock_quantity", product.stock_quantity)
        }

        price, stock, error = validate_product_data(values)

        if error:
            return jsonify({"error": error}), 400

        product.price = price
        product.stock_quantity = stock

    if "status" in data:
        if data["status"] not in ["Active", "Inactive"]:
            return jsonify({"error": "Status must be Active or Inactive"}), 400
        product.status = data["status"]

    try:
        db.session.commit()

        return jsonify({
            "message": "Product updated successfully",
            "product": product_to_dict(product)
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Product code already exists"}), 409

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not update product"}), 400


# DEACTIVATE a product instead of deleting it
@products_bp.route("/<int:product_id>", methods=["DELETE"])
@login_required
@admin_required
def deactivate_product(product_id):
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    product.status = "Inactive"

    try:
        db.session.commit()

        return jsonify({
            "message": "Product deactivated successfully"
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not deactivate product"}), 400
