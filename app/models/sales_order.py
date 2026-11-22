
from app import db
from sqlalchemy import CheckConstraint


class SalesOrder(db.Model):

    __tablename__ = "sales_orders"

    id = db.Column(db.Integer, primary_key=True)

    order_number = db.Column(db.String(50), unique=True, nullable=False)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    order_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    status = db.Column(db.String(20), default="draft", nullable=False)

    discount_percent = db.Column(
        db.Numeric(5, 2),
        default=0,
        nullable=False
    )

    subtotal = db.Column(db.Numeric(12, 2), default=0, nullable=False)

    discount_amount = db.Column(
        db.Numeric(12, 2),
        default=0,
        nullable=False
    )

    grand_total = db.Column(db.Numeric(12, 2), default=0, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 20",
            name="check_order_discount"
        ),
        CheckConstraint(
            "subtotal >= 0 AND discount_amount >= 0 AND grand_total >= 0",
            name="check_order_amounts"
        ),
    )

    customer = db.relationship("Customer", backref="sales_orders")

    user = db.relationship("User", backref="sales_orders")

    def __repr__(self):
        return f"<SalesOrder {self.order_number}>"
