from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
DB_PATH = "doubleaction.db"

# SKU prefixes for automatic generation based on category
SKU_PREFIXES = {
    "Fabrics": "FAB",
    "Pants": "PNT",
    "Vests": "VST",
    "Jackets": "JCK",
    "Shirts": "SHT",
    "Ties": "TIE"
}

# --- DATABASE HELPER ---
def get_db_connection():
    # Establishes a connection to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    # Allows accessing columns by name
    conn.row_factory = sqlite3.Row
    return conn

# --- NEW DASHBOARD ENDPOINT ---
@app.route("/dashboard/summary", methods=["GET"])
def get_dashboard_summary():
    # This endpoint provides a summary of data for the dashboard alerts.
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query 1: Find products where the quantity is at or below the minimum quantity.
    cursor.execute("SELECT name, quantity, min_quantity FROM products WHERE quantity <= min_quantity")
    low_stock_items = [dict(row) for row in cursor.fetchall()]

    # Query 2: Count orders that need attention (Pending or just received).
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'Pending' OR status = 'Order Received'")
    pending_orders_count = cursor.fetchone()['count']

    conn.close()

    summary_data = {
        "low_stock_items": low_stock_items,
        "pending_orders_count": pending_orders_count
    }
    return jsonify(summary_data)

# ---------- ORDERS API ENDPOINTS ----------

@app.route("/orders", methods=["GET"])
def get_orders():
    # --- Search and Filter Logic ---
    search_name = request.args.get('name', '')
    search_status = request.args.get('status', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT o.order_id, o.date, o.status, o.total, c.name AS customer
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
    """
    
    conditions = []
    params = []
    
    if search_name:
        conditions.append("c.name LIKE ?")
        params.append(f"%{search_name}%")
        
    if search_status:
        conditions.append("o.status = ?")
        params.append(search_status)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY o.date DESC"
    
    cursor.execute(query, params)
    
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(orders)

@app.route("/orders", methods=["POST"])
def add_order():
    data = request.json
    customer_data = data.get("customer")
    items = data.get("items", [])

    if not customer_data or not items:
        return jsonify({"error": "Missing customer or items data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT customer_id FROM customers WHERE id_number = ?", (customer_data["id_number"],))
    customer = cursor.fetchone()
    
    if customer:
        customer_id = customer["customer_id"]
    else:
        cursor.execute(
            "INSERT INTO customers (name, id_number, phone, email) VALUES (?, ?, ?, ?)",
            (customer_data["name"], customer_data["id_number"], customer_data["phone"], customer_data["email"])
        )
        customer_id = cursor.lastrowid

    # The default status 'Order Received' is set by the frontend.
    cursor.execute(
        "INSERT INTO orders (customer_id, date, status, total) VALUES (?, ?, ?, ?)",
        (customer_id, data["date"], data["status"], data["total"])
    )
    order_id = cursor.lastrowid

    for item in items:
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
            (order_id, item["product_id"], item["quantity"])
        )
        cursor.execute(
            "UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
            (item["quantity"], item["product_id"])
        )

    conn.commit()
    conn.close()
    return jsonify({"message": "Order added successfully"}), 201

# --- NEW ENDPOINT FOR STATUS UPDATE ---
@app.route("/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    # Gets the new status from the request body
    data = request.json
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Status field is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # First, check if the order actually exists
    cursor.execute("SELECT order_id FROM orders WHERE order_id = ?", (order_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    # Update the status for the given order_id
    cursor.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?",
        (new_status, order_id)
    )
    
    conn.commit()
    conn.close()

    return jsonify({"message": f"Order {order_id} status updated successfully"}), 200


# ---------- PRODUCTS API ENDPOINTS (No changes here) ----------

@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products)

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route("/products", methods=["POST"])
def add_product():
    data = request.json
    name = data.get("name")
    category = data.get("category")
    price = data.get("price")
    quantity = data.get("quantity")
    min_quantity = data.get("min_quantity")

    if not all([name, category, price is not None, quantity is not None, min_quantity is not None]):
        return jsonify({"error": "Missing product data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    prefix = SKU_PREFIXES.get(category, "GEN")
    cursor.execute("SELECT sku FROM products WHERE category = ? ORDER BY product_id DESC LIMIT 1", (category,))
    last_sku = cursor.fetchone()
    
    if last_sku and last_sku["sku"]:
        try:
            last_number = int(last_sku["sku"][-3:])
        except ValueError:
            last_number = 0
        next_number = last_number + 1
    else:
        next_number = 1

    sku = f"{prefix}{next_number:03d}"

    cursor.execute("""
        INSERT INTO products (name, category, price, quantity, min_quantity, sku)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, price, quantity, min_quantity, sku))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Product added successfully", "sku": sku}), 201

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    name = data.get("name")
    category = data.get("category")
    price = data.get("price")
    quantity = data.get("quantity")
    min_quantity = data.get("min_quantity")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, price = ?, quantity = ?, min_quantity = ?
        WHERE product_id = ?
    """, (name, category, price, quantity, min_quantity, product_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product updated successfully"})

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product deleted successfully"})

# ---------- MAIN EXECUTION ----------

if __name__ == "__main__":
    app.run(debug=True)
# This is the main entry point for the Flask application.
# It runs the Flask app in debug mode, which is useful for development.
# The app will listen for incoming requests and route them to the appropriate endpoints defined above.