\# SalesFlow ERP – Sales Order Management System



\## 1. Project Overview



SalesFlow ERP is a Flask-based Sales Order Management application developed as part of the Fresher/Trainee Software Developer Technical Assignment.



The application helps businesses manage customers, products, sales orders, inventory, stock movements, CSV product imports and sales reports.



\## 2. Technology Stack



\- Backend: Python, Flask

\- Frontend: HTML, CSS, JavaScript

\- Database: MySQL

\- ORM: Flask-SQLAlchemy

\- Authentication: Flask-Login and Werkzeug password hashing

\- API: RESTful JSON APIs

\- Testing: Pytest

\- Version Control: Git



\## 3. Main Features



\### Authentication and Roles

\- User login and logout.

\- Admin and Sales roles.

\- Password hashing.

\- Protected application routes and APIs.

\- Sales users have restricted access to orders.



\### Customer Management

\- Add customers.

\- View and edit customer details.

\- Search customers.

\- Manage active/inactive status.



\### Product Management

\- Add and edit products.

\- Search products.

\- Manage product categories and status.

\- Maintain product price and available stock.



\### Sales Order Management

\- Create draft orders with multiple products.

\- Calculate subtotal, discount and grand total.

\- Apply discounts between 0% and 20%.

\- Confirm and cancel orders.

\- Deduct stock when an order is confirmed.

\- Restore stock when a confirmed order is cancelled.



\### Inventory Management

\- Track stock movements.

\- Adjust stock with a reason.

\- Maintain inventory history.



\### CSV Import

\- Import products using CSV files.

\- Validate required columns and product data.

\- Reject invalid product records and duplicate product codes.



\### Reports

\- Customer sales summary.

\- Product sales summary.

\- Monthly sales summary.

\- Low-stock report.

\- Customers without orders.

\- Stock movement history.



\## 4. Project Structure



```text

SalesFlow-ERP/

│

├── app/

│   ├── models/

│   ├── routes/

│   ├── services/

│   ├── templates/

│   └── \_\_init\_\_.py

│

├── database/

│   ├── schema.sql

│   ├── sample\_data.sql

│   └── assignment\_queries.sql

│

├── docs/

│   └── API\_DOCUMENTATION.md

│

├── samples/

│

├── tests/

│

├── create\_users.py

├── run.py

├── requirements.txt

├── .env.example

├── .gitignore

└── AI\_USAGE.md

```



\## 5. Installation and Setup



\### Prerequisites

\- Python 3.10 or later.

\- MySQL Server.

\- Git.



\### Clone the Repository



```bash

git clone YOUR\_REPOSITORY\_URL

cd SalesFlow-ERP

```



Replace `YOUR\_REPOSITORY\_URL` with the actual repository URL.



\### Create a Virtual Environment



Windows PowerShell:



```powershell

python -m venv venv

.\\venv\\Scripts\\Activate.ps1

```



\### Install Dependencies



```powershell

pip install -r requirements.txt

```



\### Configure MySQL



1\. Create a MySQL database.

2\. Configure the database connection in your `.env` file.

3\. Refer to `database/schema.sql` for the database structure.

4\. Refer to `database/sample\_data.sql` for demonstration records.



Example `.env` configuration:



```env

SECRET\_KEY=replace\_with\_a\_secure\_random\_secret

DATABASE\_URL=mysql+pymysql://username:password@localhost:3306/salesflow\_erp

```



Replace the example values with your own local configuration. Do not commit `.env` or real credentials to Git.



\### Create User Accounts



After configuring the database and creating the tables, run:



```powershell

python create\_users.py

```



This creates the demonstration Admin and Sales accounts with hashed passwords.



\*\*Demonstration credentials:\*\*



| Role | Username | Password |

|---|---|---|

| Admin | admin | Admin@123 |

| Sales | sales | Sales@123 |



Change these demonstration passwords before deploying the application.



\### Run the Application



```powershell

python run.py

```



Open the local URL printed by Flask in your browser.



\## 6. API Documentation



API endpoint details, HTTP methods and descriptions are available in:



`docs/API\_DOCUMENTATION.md`



Main API groups:



\- `/api/auth`

\- `/api/customers`

\- `/api/products`

\- `/api/orders`

\- `/api/imports`

\- `/api/inventory`

\- `/api/reports`



\## 7. SQL Reporting Queries



The five required SQL reporting queries are available in:



`database/assignment\_queries.sql`



They cover:

1\. Top three customers by confirmed sales.

2\. Top three products by confirmed quantity sold.

3\. Customers who have never placed an order.

4\. Month-wise confirmed sales.

5\. Products below a specified stock threshold.



\## 8. Automated Tests



Tests are maintained in the `tests/` directory.



Run the test suite:



```powershell

python -m pytest -q

```



\## 9. Sample CSV Files



Sample product import files are maintained in the `samples/` directory.



\- `valid\_products.csv`

\- `invalid\_products.csv`



\## 10. AI Usage Disclosure



AI assistance and review details are documented in `AI\_USAGE.md`.



\## 11. Assumptions and Limitations



\- The application uses MySQL as its database.

\- Product prices and order amounts are stored using decimal types.

\- Order calculations are performed on the backend.

\- Stock is deducted only after successful order confirmation.

\- Demonstration credentials are intended for local evaluation only.

\- Public deployment is not required for local evaluation.



\## 12. Developer



Developed as part of the Fresher/Trainee Software Developer Technical Assignment.

