
from app import db


class Customer(db.Model):

    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=True)

    phone = db.Column(db.String(20), nullable=True)

    address = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Customer {self.customer_name}>"
