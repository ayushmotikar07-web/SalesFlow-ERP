
from flask import Flask


def create_app():
    app = Flask(__name__)

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
