
from app import db
from sqlalchemy import CheckConstraint


class SalesOrderItem(db.Model):

    __tablename__ = "sales_order_items"

    id = db.Column(db.Integer, primary_key=True)

    sales_order_id = db.Column(
        db.Integer,
        db.ForeignKey("sales_orders.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)

    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    line_total = db.Column(db.Numeric(12, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_item_quantity"),
        CheckConstraint("unit_price >= 0", name="check_item_price"),
        CheckConstraint("line_total >= 0", name="check_item_total"),
        db.UniqueConstraint(
            "sales_order_id",
            "product_id",
            name="unique_product_per_order"
        ),
    )

    sales_order = db.relationship(
        "SalesOrder",
        backref="items"
    )

    product = db.relationship(
        "Product",
        backref="order_items"
    )

    def __repr__(self):
        return f"<SalesOrderItem {self.id}>"
