
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

from app.config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from app import models
    from app.models import User

    from app.routes.auth import auth_bp
    from app.routes.customers import customers_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.inventory import inventory_bp
    from app.routes.reports import reports_bp
    from app.routes.imports import imports_bp

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(imports_bp)

    @app.route("/")
    def home():
        if not current_user.is_authenticated:
            return redirect(url_for("login_page"))

        return render_template("dashboard.html")

    @app.route("/login")
    def login_page():
        if current_user.is_authenticated:
            return redirect(url_for("home"))

        return render_template("login.html")

    return app
