
from datetime import date

from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import and_, func, distinct

from app import db
from app.models.customer import Customer
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def get_date_filters():
    """Read optional YYYY-MM-DD date filters."""
    start_text = request.args.get("start_date")
    end_text = request.args.get("end_date")

    try:
        start_date = date.fromisoformat(start_text) if start_text else None
        end_date = date.fromisoformat(end_text) if end_text else None
    except ValueError:
        return None, None, (
            jsonify({"error": "Dates must use YYYY-MM-DD format"}),
            400
        )

    if start_date and end_date and start_date > end_date:
        return None, None, (
            jsonify({"error": "start_date cannot be after end_date"}),
            400
        )

    return start_date, end_date, None


def order_date_conditions(start_date, end_date):
    conditions = []
    if start_date:
        conditions.append(func.date(SalesOrder.order_date) >= start_date)
    if end_date:
        conditions.append(func.date(SalesOrder.order_date) <= end_date)
    return conditions


# 1. Customer Sales Summary
# Includes customers with zero confirmed orders.
@reports_bp.route("/customer-sales", methods=["GET"])
@login_required
def customer_sales():
    start_date, end_date, error = get_date_filters()
    if error:
        return error

    join_conditions = [
        SalesOrder.customer_id == Customer.id,
        SalesOrder.status == "Confirmed"
    ]
    join_conditions.extend(order_date_conditions(start_date, end_date))

    results = (
        db.session.query(
            Customer.id,
            Customer.customer_name,
            func.count(distinct(SalesOrder.id)).label("order_count"),
            func.coalesce(func.sum(SalesOrder.grand_total), 0).label("total_sales")
        )
        .outerjoin(SalesOrder, and_(*join_conditions))
        .group_by(Customer.id, Customer.customer_name)
        .order_by(func.coalesce(func.sum(SalesOrder.grand_total), 0).desc())
        .all()
    )

    return jsonify([
        {
            "customer_id": row.id,
            "customer_name": row.customer_name,
            "order_count": int(row.order_count or 0),
            "total_sales": float(row.total_sales or 0)
        }
        for row in results
    ]), 200


# 2. Product Sales Summary
@reports_bp.route("/product-sales", methods=["GET"])
@login_required
def product_sales():
    start_date, end_date, error = get_date_filters()
    if error:
        return error

    conditions = [SalesOrder.status == "Confirmed"]
    conditions.extend(order_date_conditions(start_date, end_date))

    results = (
        db.session.query(
            Product.id,
            Product.product_code,
            Product.product_name,
            func.coalesce(func.sum(SalesOrderItem.quantity), 0).label("quantity_sold"),
            func.coalesce(func.sum(SalesOrderItem.line_total), 0).label("total_sales")
        )
        .join(SalesOrderItem, Product.id == SalesOrderItem.product_id)
        .join(SalesOrder, SalesOrder.id == SalesOrderItem.sales_order_id)
        .filter(*conditions)
        .group_by(Product.id, Product.product_code, Product.product_name)
        .order_by(func.sum(SalesOrderItem.quantity).desc())
        .all()
    )

    return jsonify([
        {
            "product_id": row.id,
            "product_code": row.product_code,
            "product_name": row.product_name,
            "quantity_sold": int(row.quantity_sold or 0),
            "total_sales": float(row.total_sales or 0)
        }
        for row in results
    ]), 200


# 3. Monthly Confirmed Sales Summary
@reports_bp.route("/monthly-sales", methods=["GET"])
@login_required
def monthly_sales():
    results = (
        db.session.query(
            func.year(SalesOrder.order_date).label("year"),
            func.month(SalesOrder.order_date).label("month"),
            func.count(SalesOrder.id).label("order_count"),
            func.sum(SalesOrder.grand_total).label("total_sales")
        )
        .filter(SalesOrder.status == "Confirmed")
        .group_by(
            func.year(SalesOrder.order_date),
            func.month(SalesOrder.order_date)
        )
        .order_by(
            func.year(SalesOrder.order_date),
            func.month(SalesOrder.order_date)
        )
        .all()
    )

    return jsonify([
        {
            "year": int(row.year),
            "month": int(row.month),
            "order_count": int(row.order_count or 0),
            "total_sales": float(row.total_sales or 0)
        }
        for row in results
    ]), 200


# 4. Low Stock Report
@reports_bp.route("/low-stock", methods=["GET"])
@login_required
def low_stock():
    threshold_text = request.args.get("threshold", "5")

    try:
        threshold = int(threshold_text)
        if threshold < 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "threshold must be a non-negative integer"}), 400

    products = Product.query.filter(
        Product.status == "Active",
        Product.stock_quantity <= threshold
    ).order_by(Product.stock_quantity.asc()).all()

    return jsonify([
        {
            "product_id": product.id,
            "product_code": product.product_code,
            "product_name": product.product_name,
            "stock_quantity": product.stock_quantity,
            "threshold": threshold
        }
        for product in products
    ]), 200


# 5. Customers Without Orders
@reports_bp.route("/customers-without-orders", methods=["GET"])
@login_required
def customers_without_orders():
    customers = Customer.query.filter(
        ~Customer.id.in_(
            db.session.query(SalesOrder.customer_id).distinct()
        )
    ).all()

    return jsonify([
        {
            "customer_id": customer.id,
            "customer_name": customer.customer_name,
            "email": customer.email,
            "phone": customer.phone
        }
        for customer in customers
    ]), 200
