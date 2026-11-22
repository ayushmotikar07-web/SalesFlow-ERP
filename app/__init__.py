
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

from app.config import Config

db = SQLAlchemy()


from app import models
from app.models import User
from app.routes.customers import customers_bp
from app.routes.auth import auth_bp


def create_app():
    app = Flask(__name__)

   
    app.config.from_object(Config)

    
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)

    @app.route("/")
    def home():
        if not current_user.is_authenticated:
            return render_template("login.html")

        return f"""
        <html>
            <head>
                <title>SalesFlow ERP</title>
            </head>
            <body>
                <h1>Welcome to SalesFlow ERP</h1>
                <p>Logged in as: {current_user.username}</p>
                <p>Role: {current_user.role}</p>
                <form action="/api/auth/logout" method="POST">
                    <button type="submit">Logout</button>
                </form>
            </body>
        </html>
        """

    return app
