from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config


db = SQLAlchemy()

from app import models


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    @app.route("/")
    def home():
        return """
        <html>
            <head>
                <title>SalesFlow ERP</title>
            </head>
            <body>
                <h1>Welcome to SalesFlow ERP</h1>
                <p>Your Sales and Inventory Management System is starting!</p>
            </body>
        </html>
        """

    return app