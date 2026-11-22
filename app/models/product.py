
from app import db
from sqlalchemy import CheckConstraint


class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    product_code = db.Column(db.String(50), unique=True, nullable=False)

    product_name = db.Column(db.String(120), nullable=False)

    category = db.Column(db.String(100), nullable=True)

    price = db.Column(db.Numeric(10, 2), nullable=False)

    stock_quantity = db.Column(db.Integer, default=0, nullable=False)

    status = db.Column(db.String(20), default="active", nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_product_price"),
        CheckConstraint("stock_quantity >= 0", name="check_product_stock"),
    )

    def __repr__(self):
        return f"<Product {self.product_name}>"
