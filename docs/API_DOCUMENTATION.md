\# SalesFlow ERP – API Documentation



\## Base URL

`http://127.0.0.1:5000`



Authentication uses Flask-Login sessions. Log in before accessing protected endpoints and retain the session cookie.



\## 1. Authentication



| Method | Endpoint | Description |

|---|---|---|

| POST | `/api/auth/login` | Login |

| POST | `/api/auth/logout` | Logout |

| GET | `/api/auth/me` | Current user |



\## 2. Customers



| Method | Endpoint | Description |

|---|---|---|

| GET | `/api/customers/` | List/search customers |

| GET | `/api/customers/{customer\_id}` | View customer |

| POST | `/api/customers/` | Create customer |

| PUT | `/api/customers/{customer\_id}` | Update customer |

| DELETE | `/api/customers/{customer\_id}` | Delete customer |



\## 3. Products



| Method | Endpoint | Description |

|---|---|---|

| GET | `/api/products/` | List/search products |

| GET | `/api/products/{product\_id}` | View product |

| POST | `/api/products/` | Create product |

| PUT | `/api/products/{product\_id}` | Update product |

| DELETE | `/api/products/{product\_id}` | Delete product |



\## 4. Sales Orders



| Method | Endpoint | Description |

|---|---|---|

| GET | `/api/orders/` | List accessible orders |

| POST | `/api/orders/` | Create draft order |

| GET | `/api/orders/{order\_id}` | View order |

| POST | `/api/orders/{order\_id}/confirm` | Confirm order |

| POST | `/api/orders/{order\_id}/cancel` | Cancel order |



\## 5. Inventory



| Method | Endpoint | Description |

|---|---|---|

| POST | `/api/inventory/adjustments` | Adjust stock |

| GET | `/api/inventory/movements` | View stock movement history |



\## 6. CSV Product Import



| Method | Endpoint | Description |

|---|---|---|

| POST | `/api/imports/products` | Import products from CSV |



Expected CSV columns:



`product\_code,product\_name,category,price,stock\_quantity,status`



Sample files are available in the `samples` folder.



\## 7. Reports



| Method | Endpoint | Description |

|---|---|---|

| GET | `/api/reports/customer-sales` | Customer sales summary |

| GET | `/api/reports/product-sales` | Product sales summary |

| GET | `/api/reports/monthly-sales` | Monthly confirmed sales |

| GET | `/api/reports/low-stock` | Low stock report |

| GET | `/api/reports/customers-without-orders` | Customers without orders |



Customer and product reports accept optional date filters:



`?start\_date=2026-01-01\&end\_date=2026-11-23`



Low-stock report accepts:



`?threshold=5`



\## 8. Common HTTP Status Codes



| Code | Meaning |

|---|---|

| 200 | Successful request |

| 201 | Resource created |

| 400 | Invalid input |

| 401 | Authentication required |

| 403 | Permission denied |

| 404 | Resource not found |

| 409 | Conflict |

| 500 | Unexpected server error |



Exact request fields and response formats are defined by the implementation.



\## 9. Running the Application



Activate the virtual environment and run:



`python run.py`



Local URL: `http://127.0.0.1:5000`

s

