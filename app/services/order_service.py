
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from uuid import uuid4

from app import db
from app.models import (
    Customer,
    Product,
    SalesOrder,
    SalesOrderItem,
    StockMovement
)


CENT = Decimal("0.01")


def money(value):
    return Decimal(str(value)).quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )


def create_draft_order(customer_id, user_id, items, discount_percent=0):
    try:
        if isinstance(customer_id, bool):
            raise ValueError("Invalid customer ID")

        customer_id = int(customer_id)

        if customer_id <= 0:
            raise ValueError("Invalid customer ID")

        if not isinstance(items, list) or not items:
            raise ValueError("An order must contain at least one product")

        customer = db.session.get(Customer, customer_id)

        if not customer or not customer.is_active:
            raise ValueError("Customer not found or inactive")

        try:
            discount = Decimal(str(discount_percent))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Invalid discount percentage")

        if not discount.is_finite() or discount < 0 or discount > 20:
            raise ValueError("Discount must be between 0 and 20 percent")

        seen_products = set()
        prepared_items = []
        subtotal = Decimal("0.00")

        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each order item must be an object")

            try:
                product_id = int(item.get("product_id"))
                quantity = int(item.get("quantity"))
            except (TypeError, ValueError):
                raise ValueError("Product ID and quantity must be whole numbers")

            if isinstance(item.get("product_id"), bool) or isinstance(item.get("quantity"), bool):
                raise ValueError("Product ID and quantity must be whole numbers")

            if product_id <= 0:
                raise ValueError("Invalid product ID")

            if quantity <= 0:
                raise ValueError("Product quantity must be greater than zero")

            if product_id in seen_products:
                raise ValueError("Duplicate products are not allowed in an order")

            seen_products.add(product_id)

            product = db.session.get(Product, product_id)

            if not product or product.status != "Active":
                raise ValueError(
                    f"Product with ID {product_id} is not available"
                )

            unit_price = money(product.price)
            line_total = money(unit_price * quantity)
            subtotal += line_total

            prepared_items.append({
                "product_id": product.id,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": line_total
            })

        subtotal = money(subtotal)
        discount_amount = money(subtotal * discount / Decimal("100"))
        grand_total = money(subtotal - discount_amount)

        order = SalesOrder(
            order_number=f"SO-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}",
            customer_id=customer.id,
            user_id=user_id,
            order_date=datetime.utcnow(),
            status="Draft",
            discount_percent=discount,
            subtotal=subtotal,
            discount_amount=discount_amount,
            grand_total=grand_total
        )

        db.session.add(order)
        db.session.flush()

        for item in prepared_items:
            db.session.add(SalesOrderItem(
                sales_order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                line_total=item["line_total"]
            ))

        db.session.commit()
        return order

    except ValueError:
        db.session.rollback()
        raise

    except Exception:
        db.session.rollback()
        raise


def confirm_order(order_id, user_id):
    try:
        # Lock the order so two requests cannot confirm it simultaneously
        order = (
            db.session.query(SalesOrder)
            .filter_by(id=order_id)
            .with_for_update()
            .first()
        )

        if not order:
            raise ValueError("Order not found")

        if order.status != "Draft":
            raise ValueError(
                f"Only Draft orders can be confirmed. Current status: {order.status}"
            )

        items = (
            SalesOrderItem.query
            .filter_by(sales_order_id=order.id)
            .order_by(SalesOrderItem.product_id)
            .all()
        )

        if not items:
            raise ValueError("Order has no products")

        product_ids = [item.product_id for item in items]

        # Lock all products in a consistent order to protect stock
        products = (
            Product.query
            .filter(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
            .all()
        )

        product_map = {product.id: product for product in products}

        # Check every product before deducting anything
        for item in items:
            product = product_map.get(item.product_id)

            if not product or product.status != "Active":
                raise ValueError(
                    f"Product ID {item.product_id} is missing or inactive"
                )

            if product.stock_quantity < item.quantity:
                raise ValueError(
                    f"Insufficient stock for {product.product_name}. "
                    f"Available: {product.stock_quantity}, "
                    f"Required: {item.quantity}"
                )

        # Deduct stock and record movements
        for item in items:
            product = product_map[item.product_id]
            product.stock_quantity -= item.quantity

            movement = StockMovement(
                product_id=product.id,
                movement_type="SALE",
                quantity_change=-item.quantity,
                reference_type="Sales Order",
                reference_id=order.id,
                reason=f"Stock deducted for order {order.order_number}",
                user_id=user_id
            )

            db.session.add(movement)

        order.status = "Confirmed"
        db.session.commit()

        return order

    except ValueError:
        db.session.rollback()
        raise

    except Exception:
        db.session.rollback()
        raise


def cancel_order(order_id, user_id):
    try:
        order = (
            db.session.query(SalesOrder)
            .filter_by(id=order_id)
            .with_for_update()
            .first()
        )

        if not order:
            raise ValueError("Order not found")

        if order.status == "Cancelled":
            raise ValueError("Order is already cancelled")

        if order.status not in ["Draft", "Confirmed"]:
            raise ValueError("This order cannot be cancelled")

        items = (
            SalesOrderItem.query
            .filter_by(sales_order_id=order.id)
            .order_by(SalesOrderItem.product_id)
            .all()
        )

        # Draft orders have not deducted stock
        if order.status == "Confirmed":
            product_ids = [item.product_id for item in items]

            products = (
                Product.query
                .filter(Product.id.in_(product_ids))
                .order_by(Product.id)
                .with_for_update()
                .all()
            )

            product_map = {product.id: product for product in products}

            if len(product_map) != len(set(product_ids)):
                raise ValueError("A product from this order no longer exists")

            for item in items:
                product = product_map[item.product_id]
                product.stock_quantity += item.quantity

                movement = StockMovement(
                    product_id=product.id,
                    movement_type="SALE_RETURN",
                    quantity_change=item.quantity,
                    reference_type="Sales Order",
                    reference_id=order.id,
                    reason=f"Stock restored after cancelling order {order.order_number}",
                    user_id=user_id
                )

                db.session.add(movement)

        order.status = "Cancelled"
        db.session.commit()

        return order

    except ValueError:
        db.session.rollback()
        raise

    except Exception:
        db.session.rollback()
        raise
