# Inventory Management System

This **Inventory Management System** is a web-based application built with Django and Bootstrap 5. It allows users to efficiently manage products, suppliers, sales orders, and stock movements.

## Features
1. **Product Management**: Add, edit, delete, and list products with supplier details and stock quantity.
2. **Supplier Management**: Maintain a supplier database with contact information and addresses.
3. **Sales Orders**: Create, view, complete, and cancel sale orders.
4. **Stock Movement**: Track product stock inflow and outflow with movement history.
5. **Responsive Design**: Modern, user-friendly interface optimized for all devices.

## Technology Stack
- **Backend**: Django (Python)
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Database**: SQLite (default, easily switchable)

## How to Run
1. Clone the repository and navigate to the project directory.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the server: `python manage.py runserver`.
4. Access the app at `http://127.0.0.1:8000/`.

Enjoy managing your inventory with ease!

(penv) C:\Users\Yashu\Downloads\MISHI_PAY\myproject>python manage.py makemigrations
No changes detected

(penv) C:\Users\Yashu\Downloads\MISHI_PAY\myproject>python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, inventory, sessions
Running migrations:
  No migrations to apply.