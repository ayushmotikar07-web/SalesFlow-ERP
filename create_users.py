
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():

    
    admin = User(
        username="admin",
        email="admin@salesflow.com",
        role="Admin",
        is_active=True
    )
    admin.set_password("Admin@123")

    
    sales = User(
        username="sales",
        email="sales@salesflow.com",
        role="Sales",
        is_active=True
    )
    sales.set_password("Sales@123")

    db.session.add_all([admin, sales])
    db.session.commit()

    print("Admin and Sales User accounts created successfully!")
