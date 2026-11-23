
import io

from app import db
from app.models import Product


def test_invalid_csv_imports_nothing(
    app, client, admin, login_as
):
    with app.app_context():
        login_as(admin)

        csv_content = (
            "product_code,product_name,category,price,stock_quantity,status\n"
            "CSV001,Keyboard,Electronics,800,10,Active\n"
            "CSV002,Monitor,Electronics,-500,5,Active\n"
        )

        response = client.post(
            "/api/imports/products",
            data={
                "file": (
                    io.BytesIO(csv_content.encode("utf-8")),
                    "invalid_test.csv",
                )
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        assert Product.query.count() == 0
        assert "No products were imported" in response.get_json()["error"]
