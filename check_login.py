
from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username="admin").first()

    if user is None:
        print("PROBLEM: Admin user not found in database.")
    else:
        print("Admin user found!")
        print("Username:", user.username)
        print("Role:", user.role)
        print("Active:", user.is_active)

        if user.check_password("Admin@123"):
            print("PASSWORD: Correct!")
        else:
            print("PASSWORD: Incorrect!")
