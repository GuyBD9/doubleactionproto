import sqlite3

# This script sets up the database schema.
# Run this script ONCE after deleting the old .db file.

conn = sqlite3.connect('doubleaction.db')
cursor = conn.cursor()

# --- Customers Table ---
# Using 'customer_id' as the primary key and 'id_number' for the user-provided ID.
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_number TEXT UNIQUE NOT NULL,
    phone TEXT,
    email TEXT
)
''')

# --- Products Table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    quantity INTEGER,
    min_quantity INTEGER
)
''')

# --- Orders Table ---
# IMPORTANT FIX: The column is named 'date', not 'order_date'.
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    date TEXT,
    status TEXT,
    total REAL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
)
''')

# --- Order Items Table (Link between orders and products) ---
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

conn.commit()
conn.close()
print("Database 'doubleaction.db' and its tables were created successfully.")
