import sqlite3

# This script sets up the database schema with detailed timestamps.
# Run this script ONCE after deleting the old .db file.

conn = sqlite3.connect('doubleaction.db')
cursor = conn.cursor()

# --- Customers Table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_number TEXT UNIQUE NOT NULL,
    phone TEXT,
    email TEXT,
    street TEXT,
    city TEXT,
    postal_code TEXT
)
''')

# --- Products Table ---
# ADDED: creation_timestamp column.
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    quantity INTEGER,
    min_quantity INTEGER,
    creation_timestamp TEXT,
    last_updated_timestamp TEXT,
    last_ordered_timestamp TEXT
)
''')

# --- Orders Table ---
# ADDED: both creation and update timestamps for full traceability.
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    date TEXT,
    status TEXT,
    total REAL,
    creation_timestamp TEXT,
    last_updated_timestamp TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
)
''')

# --- Order Items Table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
)
''')

# --- Suppliers Table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contact_name TEXT,
    email TEXT,
    phone TEXT
)
''')

# --- Order Logs Table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    action TEXT,
    timestamp TEXT,
    FOREIGN KEY(order_id) REFERENCES orders(order_id)
)
''')

# --- Product Logs Table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS product_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    quantity_change INTEGER,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
''')

# --- Users Table ---
# ADDED: Secure user management with hashed passwords and roles.
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'employee'))
)
''')


conn.commit()
conn.close()
print("Database 'doubleaction.db' and its tables were created successfully with all customer address fields order_logs, and product_logs.")
