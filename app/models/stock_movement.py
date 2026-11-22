
from app import db
from sqlalchemy import CheckConstraint


class StockMovement(db.Model):

    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    movement_type = db.Column(db.String(30), nullable=False)

    quantity_change = db.Column(db.Integer, nullable=False)

    reference_type = db.Column(db.String(30), nullable=True)

    reference_id = db.Column(db.Integer, nullable=True)

    reason = db.Column(db.String(255), nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "quantity_change != 0",
            name="check_stock_movement_quantity"
        ),
    )

    product = db.relationship("Product", backref="stock_movements")

    user = db.relationship("User", backref="stock_movements")

    def __repr__(self):
        return f"<StockMovement {self.id}>"
