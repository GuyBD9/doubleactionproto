# DOUBLE ACTION ONE – Admin Management System

A complete web-based ERP designed for the luxury fashion brand **Double Action**. This system provides a robust admin panel to manage inventory, track customer orders, and view real-time business analytics, tailored for the high-end menswear and grooms' fashion market.

The project was developed as part of the Information Systems Design course, demonstrating a full-stack application with a secure, server-side architecture.

## ✨ Features

This system is packed with features designed to streamline business operations:

#### 🔐 **Secure Authentication & Access Control**

- **Server-Side Sessions**: Secure login system with server-side session management.
- **Hashed Passwords**: User credentials are fully encrypted using `werkzeug.security`.
- **Role-Based Access**: Differentiated access levels for **Admin** (full CRUD) and **Employee** roles.

#### 📦 **Advanced Inventory Management**

- **Full Product CRUD**: Create, Read, Update, and Delete products with an intuitive interface.
- **Dynamic Filtering & Search**: Instantly find products by name, SKU, or category.
- **Low Stock Alerts**: Automatic highlighting of items below their minimum quantity on the dashboard and in the inventory table.
- **Automated SKU Generation**: SKUs are automatically created based on product category (e.g., "SHT" for Shirts).
- **Detailed Logging**: Every change in stock quantity is logged, whether from a manual update or a new order.

#### 🛒 **Comprehensive Order Management**

- **Full Order CRUD**: Create, read, and edit orders for new or existing customers.
- **Interactive Status Updates**: Update order status (`Pending`, `Shipped`, `Delivered`) via a user-friendly modal.
- **Automatic Inventory Sync**: Inventory levels are automatically adjusted when an order is created or edited.
- **Order History**: View a complete log of all changes and status updates for every order.

#### 📊 **Analytics & Data Export**

- **Live Dashboard**: The main dashboard provides a high-level summary of pending orders and low-stock items.
- **Visual Analytics**: A dedicated analytics page displays charts for "Sales by Category" and "Top 5 Best-Selling Items".
- **Excel Export**: Export the entire inventory list, product logs, or a comprehensive list of all customer orders to a formatted Excel file with a single click.

---

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite
- **Data Tools**: Pandas, XlsxWriter
- **Security**: Werkzeug (Password Hashing), Flask Sessions

---

## 🚀 Getting Started (Simplified)

This project includes a setup script that automates the entire installation process.

### Prerequisites

- Make sure you have **Python 3.8+** installed. You can check with `python --version`.

### One-Step Installation & Launch

1.  **Clone the project:**
    ```bash
    git clone [https://github.com/GuyBD9/doubleactionproto.git](https://github.com/GuyBD9/doubleactionproto.git)
    cd doubleactionproto
    ```
2.  **Run the local setup script:**
    ```bash
    python run_local.py
    ```
    This script will automatically:
    - Install all required dependencies from `requirements.txt`.
    - Check if the `doubleaction.db` database exists.
    - If not, it will create the database and seed it with sample data.
    - Start the Flask server.

---

## 🔑 Usage

1.  Once the server is running, open the system in your browser at:
    **[http://127.0.0.1:5000/login.html](http://127.0.0.1:5000/login.html)**

2.  Log in with one of the following credentials:

- **Admin Role** 👨‍💻

  - **Username**: `admin`
  - **Password**: `admin123`

- **Employee Role** 👨‍💼
  - **Username**: `employee`
  - **Password**: `emp123`

### Final Notes

- Always access the system through the server URL (`http://127.0.0.1:5000/...`). Do **NOT** open the HTML files directly in your browser (`file:///...`).
- To stop the server, press `CTRL+C` in the terminal where it is running.
