
import csv
import io
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement

imports_bp = Blueprint("imports", __name__, url_prefix="/api/imports")

REQUIRED_HEADERS = [
    "product_code",
    "product_name",
    "category",
    "price",
    "stock_quantity",
    "status"
]


@imports_bp.route("/products", methods=["POST"])
@login_required
def import_products():
    if current_user.role != "Admin":
        return jsonify({"error": "Admin access required"}), 403

    uploaded_file = request.files.get("file")

    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"error": "Please upload a CSV file"}), 400

    if not uploaded_file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are allowed"}), 400

    try:
        content = uploaded_file.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))

        if reader.fieldnames != REQUIRED_HEADERS:
            return jsonify({
                "error": "CSV headers do not match the required format",
                "required_headers": REQUIRED_HEADERS,
                "received_headers": reader.fieldnames
            }), 400

        rows = []
        errors = []
        seen_codes = set()

        for row_number, row in enumerate(reader, start=2):
            code = (row.get("product_code") or "").strip()
            name = (row.get("product_name") or "").strip()
            category = (row.get("category") or "").strip()
            price_text = (row.get("price") or "").strip()
            stock_text = (row.get("stock_quantity") or "").strip()
            status = (row.get("status") or "").strip()

            if not any([code, name, category, price_text, stock_text, status]):
                continue

            row_errors = []

            if not code:
                row_errors.append("Product code is required")

            if not name:
                row_errors.append("Product name is required")

            if not category:
                row_errors.append("Category is required")

            try:
                price = Decimal(price_text)
                if not price.is_finite() or price < 0:
                    row_errors.append("Price must be a non-negative number")
                elif price.as_tuple().exponent < -2:
                    row_errors.append("Price cannot have more than 2 decimal places")
            except InvalidOperation:
                price = None
                row_errors.append("Invalid price")

            try:
                if not stock_text or not stock_text.isdigit():
                    raise ValueError()
                stock = int(stock_text)
            except ValueError:
                stock = None
                row_errors.append("Stock quantity must be a non-negative whole number")

            if status not in ("Active", "Inactive"):
                row_errors.append("Status must be Active or Inactive")

            normalized_code = code.casefold()

            if code and normalized_code in seen_codes:
                row_errors.append("Duplicate product code in CSV")
            elif code:
                seen_codes.add(normalized_code)

            if code and Product.query.filter_by(product_code=code).first():
                row_errors.append("Product code already exists in database")

            if row_errors:
                errors.append({
                    "row": row_number,
                    "product_code": code,
                    "errors": row_errors
                })
            else:
                rows.append({
                    "product_code": code,
                    "product_name": name,
                    "category": category,
                    "price": price,
                    "stock_quantity": stock,
                    "status": status
                })

        if errors:
            return jsonify({
                "error": "Import rejected. No products were imported.",
                "row_errors": errors
            }), 400

        if not rows:
            return jsonify({"error": "CSV contains no product records"}), 400

        imported_count = 0

        for row in rows:
            product = Product(
                product_code=row["product_code"],
                product_name=row["product_name"],
                category=row["category"],
                price=row["price"],
                stock_quantity=row["stock_quantity"],
                status=row["status"]
            )

            db.session.add(product)
            db.session.flush()

            if row["stock_quantity"] > 0:
                movement = StockMovement(
                    product_id=product.id,
                    movement_type="OPENING_STOCK",
                    quantity_change=row["stock_quantity"],
                    reference_type="CSV Import",
                    reference_id=None,
                    reason="Opening stock from CSV import",
                    user_id=current_user.id
                )
                db.session.add(movement)

            imported_count += 1

        db.session.commit()

        return jsonify({
            "message": "Products imported successfully",
            "imported_count": imported_count
        }), 201

    except UnicodeDecodeError:
        db.session.rollback()
        return jsonify({"error": "CSV must use UTF-8 encoding"}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Import failed. No products were imported."}), 500
