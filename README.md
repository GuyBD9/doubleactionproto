
# DOUBLE ACTION ONE – Admin Management System

This is the admin panel for **Double Action**, a luxury fashion brand for grooms and formal menswear. The system is a web-based ERP designed to manage inventory, track customer orders, and view real-time analytics.

-----

## ✨ Features

  * **Inventory Management**:

      * Full CRUD (Create, Read, Update, Delete) functionality for all products.
      * Automatic SKU generation based on product category (e.g., "SHT" for Shirts).
      * Tracks `creation`, `last_updated`, and `last_ordered` timestamps for every item.
      * A detailed logging system (`product_logs`) tracks every quantity change, whether from a manual update or a customer order.
      * View low-stock items highlighted in the inventory table and on the dashboard.

  * **Order Management**:

      * Create new orders for new or existing customers.
      * Full CRUD for orders, including editing items and customer details on existing orders.
      * Update order status (`Pending`, `Shipped`, `Delivered`, etc.) with changes automatically logged.
      * Inventory levels are automatically adjusted when an order is created or edited.

  * **Analytics & Dashboard**:

      * A dashboard that provides a high-level summary of business operations, including pending orders and low-stock alerts.
      * Visual charts showing sales performance, including "Sales by Category" and "Top 5 Best-Selling Items".

  * **Data Export**:

      * Export the entire inventory list and product logs to a formatted Excel file.
      * Export a comprehensive list of all customer orders, including customer details and items, to an Excel file.

-----

## 🛠️ Technology Stack

  * **Backend**: Python, Flask
  * **Database**: SQLite
  * **Data Export/Handling**: Pandas, XlsxWriter
  * **Frontend**: HTML, Bootstrap 5, JavaScript (for API calls and DOM manipulation)

-----

## 🚀 Getting Started

To run this system locally on your computer:

### 1\. Clone the project

```bash
git clone https://github.com/GuyBD9/doubleactionproto.git
cd doubleactionproto
```

-----

## 🧰 Setup Instructions (Mac & Windows)

### 📍 Prerequisite:

Make sure you have **Python 3.8+** installed. You can check with:

```bash
python3 --version  # or python --version on Windows
```

#### 💻 Mac Users

1.  **Open Terminal** and navigate to the project folder.
2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up and seed the database:
    ```bash
    python database_setup.py
    python seed_database.py
    ```
5.  Run the Flask server:
    ```bash
    python app.py
    ```

#### 🪟 Windows Users

1.  **Open CMD or PowerShell** and go to the project folder.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up and seed the database:
    ```bash
    python database_setup.py
    python seed_database.py
    ```
5.  Run the Flask server:
    ```bash
    python app.py
    ```

-----

## 🔑 Usage

1.  Once the server is running, open the system in your browser at:
    **[http://127.0.0.1:5000/login.html](https://www.google.com/search?q=http://127.0.0.1:5000/login.html)**

2.  Log in with one of the following credentials:

      * **Role**: Admin
          * **Username**: `admin`
          * **Password**: `admin123`
      * **Role**: Employee
          * **Username**: `employee`
          * **Password**: `emp123`

### ✅ Final Notes

  - Do **NOT** double-click `login.html` or open it with `file:///` — this will prevent the backend server from working correctly.
  - Make sure the Flask server is running in your terminal before trying to access the system in your browser.