
import pytest

from app import db
from app.models import (
    Product,
    SalesOrder,
    SalesOrderItem,
    StockMovement,
)
from app.services.order_service import (
    create_draft_order,
    confirm_order,
    cancel_order,
)


def make_order(customer_id, user_id, product_id, quantity=2, discount=0):
    return create_draft_order(
        customer_id=customer_id,
        user_id=user_id,
        items=[
            {
                "product_id": product_id,
                "quantity": quantity,
            }
        ],
        discount_percent=discount,
    )


def test_multi_product_order_with_discount(app, admin, customer, product):
    with app.app_context():
        second_product = Product(
            product_code="TEST002",
            product_name="Test Mouse",
            category="Electronics",
            price=500,
            stock_quantity=10,
            status="Active",
        )
        db.session.add(second_product)
        db.session.commit()

        order = create_draft_order(
            customer_id=customer,
            user_id=admin,
            items=[
                {"product_id": product, "quantity": 2},
                {"product_id": second_product.id, "quantity": 1},
            ],
            discount_percent=10,
        )

        assert order.status == "Draft"
        assert float(order.subtotal) == 2500.00
        assert float(order.discount_amount) == 250.00
        assert float(order.grand_total) == 2250.00
        assert len(order.items) == 2


def test_invalid_quantity_rejected(app, admin, customer, product):
    with app.app_context():
        with pytest.raises(ValueError):
            make_order(customer, admin, product, quantity=0)

        assert SalesOrder.query.count() == 0


def test_discount_above_20_rejected(app, admin, customer, product):
    with app.app_context():
        with pytest.raises(ValueError):
            make_order(
                customer,
                admin,
                product,
                quantity=1,
                discount=25,
            )

        assert SalesOrder.query.count() == 0


def test_confirm_order_deducts_stock(app, admin, customer, product):
    with app.app_context():
        order = make_order(customer, admin, product, quantity=3)

        confirm_order(order.id, admin)

        updated_product = db.session.get(Product, product)

        assert order.status == "Confirmed"
        assert updated_product.stock_quantity == 17

        movement = StockMovement.query.filter_by(
            reference_id=order.id,
            movement_type="SALE",
        ).first()

        assert movement is not None
        assert movement.quantity_change == -3


def test_insufficient_stock_rolls_back(app, admin, customer, product):
    with app.app_context():
        order = make_order(customer, admin, product, quantity=25)

        with pytest.raises(ValueError):
            confirm_order(order.id, admin)

        db.session.expire_all()

        updated_product = db.session.get(Product, product)
        updated_order = db.session.get(SalesOrder, order.id)

        assert updated_product.stock_quantity == 20
        assert updated_order.status == "Draft"
        assert StockMovement.query.filter_by(
            reference_id=order.id
        ).count() == 0


def test_repeated_confirmation_does_not_deduct_twice(
    app, admin, customer, product
):
    with app.app_context():
        order = make_order(customer, admin, product, quantity=4)

        confirm_order(order.id, admin)

        with pytest.raises(ValueError):
            confirm_order(order.id, admin)

        db.session.expire_all()

        updated_product = db.session.get(Product, product)

        assert updated_product.stock_quantity == 16
        assert StockMovement.query.filter_by(
            reference_id=order.id,
            movement_type="SALE",
        ).count() == 1


def test_cancelling_confirmed_order_restores_stock_once(
    app, admin, customer, product
):
    with app.app_context():
        order = make_order(customer, admin, product, quantity=5)

        confirm_order(order.id, admin)
        cancel_order(order.id, admin)

        db.session.expire_all()

        updated_product = db.session.get(Product, product)

        assert updated_product.stock_quantity == 20
        assert db.session.get(SalesOrder, order.id).status == "Cancelled"

        with pytest.raises(ValueError):
            cancel_order(order.id, admin)

        db.session.expire_all()

        assert db.session.get(Product, product).stock_quantity == 20

        assert StockMovement.query.filter_by(
            reference_id=order.id,
            movement_type="SALE_RETURN",
        ).count() == 1


def test_sales_user_cannot_access_another_users_order(
    app, client, admin, sales_user, customer, product, login_as
):
    with app.app_context():
        order = make_order(customer, admin, product, quantity=1)
        order_id = order.id

    login_as(sales_user)

    response = client.get(f"/api/orders/{order_id}")

    assert response.status_code == 403
