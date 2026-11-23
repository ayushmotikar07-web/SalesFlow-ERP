
import os
import pytest

# Set these BEFORE importing the application.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "salesflow-test-secret"

from app import create_app, db
from app.models import User, Customer, Product


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="salesflow-test-secret",
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin(app):
    with app.app_context():
        user = User(
            username="testadmin",
            email="admin@test.com",
            role="Admin",
            is_active=True,
        )
        user.set_password("Admin@123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture()
def sales_user(app):
    with app.app_context():
        user = User(
            username="testsales",
            email="sales@test.com",
            role="Sales",
            is_active=True,
        )
        user.set_password("Sales@123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture()
def customer(app):
    with app.app_context():
        record = Customer(
            customer_name="Test Customer",
            email="customer@test.com",
            phone="9000000000",
            is_active=True,
        )
        db.session.add(record)
        db.session.commit()
        return record.id


@pytest.fixture()
def product(app):
    with app.app_context():
        record = Product(
            product_code="TEST001",
            product_name="Test Laptop",
            category="Electronics",
            price=1000,
            stock_quantity=20,
            status="Active",
        )
        db.session.add(record)
        db.session.commit()
        return record.id


@pytest.fixture()
def login_as(client):
    def _login(user_id):
        with client.session_transaction() as session:
            session["_user_id"] = str(user_id)
            session["_fresh"] = True
    return _login
