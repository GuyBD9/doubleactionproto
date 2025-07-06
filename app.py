from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime  # Ensure datetime is imported
from flask import Flask, redirect
from flask import send_from_directory
import os
from flask import send_file
import pandas as pd
import io
from io import BytesIO

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
DB_PATH = "doubleaction.db"

# SKU prefixes (unchanged)
SKU_PREFIXES = {
    "Fabrics": "FAB", "Pants": "PNT", "Vests": "VST",
    "Jackets": "JCK", "Shirts": "SHT", "Ties": "TIE"
}

@app.route('/login')
def login_page():
    return send_from_directory(os.path.abspath(os.getcwd()), 'login.html')

@app.route('/<path:filename>')
def static_html(filename):
    return send_from_directory(os.path.abspath(os.getcwd()), filename)

# --- DATABASE HELPER ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- ANALYTICS AND DASHBOARD ENDPOINTS (Unchanged) ---
@app.route("/analytics/summary", methods=["GET"])
def get_analytics_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT p.category, SUM(oi.quantity * p.price) as total_sales FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.category ORDER BY total_sales DESC")
    sales_by_category = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT p.name, SUM(oi.quantity) as total_quantity_sold FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.name ORDER BY total_quantity_sold DESC LIMIT 5")
    top_selling_products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({ "sales_by_category": sales_by_category, "top_selling_products": top_selling_products })

@app.route("/dashboard/summary", methods=["GET"])
def get_dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity, min_quantity FROM products WHERE quantity <= min_quantity")
    low_stock_items = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'Pending' OR status = 'Order Received'")
    pending_orders_count = cursor.fetchone()['count']
    conn.close()
    return jsonify({ "low_stock_items": low_stock_items, "pending_orders_count": pending_orders_count })


# ---------- ORDERS API ENDPOINTS ----------


@app.route("/orders", methods=["GET"])
def get_orders():
    # This function is correct and already fetches the timestamp columns
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT o.order_id, o.date, o.status, o.total, c.name AS customer, o.creation_timestamp, o.last_updated_timestamp FROM orders o JOIN customers c ON o.customer_id = c.customer_id"
    search_name = request.args.get('name', '')
    search_status = request.args.get('status', '')
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
    query += " ORDER BY o.order_id DESC"
    cursor.execute(query, params)
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(orders)

# --- Get single order details ---
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # שליפת פרטי ההזמנה
    cursor.execute("""
        SELECT o.order_id, o.date, o.status, o.total, 
               c.name AS customer_name, c.id_number, c.phone, c.email,
               c.street, c.city, c.postal_code
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = ?
    """, (order_id,))
    order = cursor.fetchone()

    if not order:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    # שליפת הפריטים שבהזמנה
    cursor.execute("""
        SELECT oi.product_id, p.name, oi.quantity, p.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    """, (order_id,))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "order_id": order["order_id"],
        "date": order["date"],
        "status": order["status"],
        "total": order["total"],
        "customer": {
            "name": order["customer_name"],
            "id_number": order["id_number"],
            "phone": order["phone"],
            "email": order["email"],
            "street": order["street"],
            "city": order["city"],
            "postal_code": order["postal_code"]
        },
        "items": items
    })

@app.route("/orders", methods=["POST"])
def add_order():
    data = request.json
    customer_data = data.get("customer")
    items = data.get("items", [])
    if not customer_data or not items:
        return jsonify({"error": "Missing customer or items data"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Retrieve or create customer
    cursor.execute("SELECT customer_id FROM customers WHERE id_number = ?", (customer_data["id_number"],))
    customer = cursor.fetchone()
    if customer:
        customer_id = customer["customer_id"]
    else:
        cursor.execute("""
            INSERT INTO customers (name, id_number, phone, email, street, city, postal_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_data["name"], customer_data["id_number"],
            customer_data["phone"], customer_data["email"],
            customer_data.get("street"), customer_data.get("city"),
            customer_data.get("postal_code")
        ))
        customer_id = cursor.lastrowid
    
    # Current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create new order
    cursor.execute("""
        INSERT INTO orders (customer_id, date, status, total, creation_timestamp, last_updated_timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_id, data["date"], data["status"], data["total"], timestamp, timestamp))
    order_id = cursor.lastrowid
    
    # Add items, update inventory, and log changes
    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (order_id, product_id, quantity))

        cursor.execute("""
            UPDATE products SET quantity = quantity - ? WHERE product_id = ?
        """, (quantity, product_id))

        cursor.execute("""
            UPDATE products SET last_ordered_timestamp = ? WHERE product_id = ?
        """, (timestamp, product_id))

        # Log inventory change in product_logs
        cursor.execute("""
            INSERT INTO product_logs (product_id, action, quantity_change, timestamp)
            VALUES (?, ?, ?, ?)
        """, (product_id, "Order Placement", -quantity, timestamp))

    # Log order creation
    cursor.execute("""
        INSERT INTO order_logs (order_id, action, timestamp)
        VALUES (?, ?, ?)
    """, (order_id, "Order created", timestamp))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Order added successfully"}), 201

@app.route("/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    # --- THIS FUNCTION IS NOW FIXED ---
    data = request.json
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the current timestamp for the update action
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update both the status and the last_updated_timestamp
    cursor.execute("UPDATE orders SET status = ?, last_updated_timestamp = ? WHERE order_id = ?", (new_status, timestamp, order_id))
    
    cursor.execute("INSERT INTO order_logs (order_id, action, timestamp) VALUES (?, ?, ?)", (order_id, f"Status changed to {new_status}", timestamp))
    
    # Check if the update affected any row. If not, the order was not found.
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Order not found"}), 404
        
    conn.commit()
    conn.close()
    return jsonify({"message": "Order status updated"}), 200

# ---- Edit Order endpoint ----
@app.route("/orders/<int:order_id>", methods=["PUT"])
def edit_order(order_id):
    data = request.json
    customer_data = data.get("customer")
    items = data.get("items", [])
    date = data.get("date")
    total = data.get("total")

    if not customer_data or not items:
        return jsonify({"error": "Missing customer or items data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # --- Transaction Start ---

        # 1. Update customer details
        cursor.execute("""
            UPDATE customers SET name = ?, id_number = ?, phone = ?, email = ?, street = ?, city = ?, postal_code = ?
            WHERE customer_id = (SELECT customer_id FROM orders WHERE order_id = ?)
        """, (
            customer_data["name"], customer_data["id_number"], customer_data["phone"], customer_data["email"],
            customer_data.get("street"), customer_data.get("city"), customer_data.get("postal_code"), order_id))

        # 2. Update order details (date, total, and last_updated timestamp)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE orders SET date = ?, total = ?, last_updated_timestamp = ?
            WHERE order_id = ?
        """, (date, total, timestamp, order_id))

        # 3. Inventory Balancing: Restore inventory for old items
        cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = ?", (order_id,))
        old_items = cursor.fetchall()
        for item in old_items:
            cursor.execute("UPDATE products SET quantity = quantity + ? WHERE product_id = ?", (item["quantity"], item["product_id"]))

        # 4. Delete existing items from the order
        cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))

        # 5. Insert updated items and DECREASE inventory for new items
        for item in items:
            # Insert the new item into the order
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                           (order_id, item["product_id"], item["quantity"]))
            # Decrease the stock for the new/updated item quantity
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
                           (item["quantity"], item["product_id"]))
            cursor.execute("UPDATE products SET last_ordered_timestamp = ? WHERE product_id = ?", (timestamp, item["product_id"]))

        # 6. Log the update action
        cursor.execute("INSERT INTO order_logs (order_id, action, timestamp) VALUES (?, ?, ?)",
                       (order_id, "Order edited", timestamp))

        conn.commit()
        # --- Transaction End ---
        
        return jsonify({"message": "Order updated successfully"})

    except sqlite3.Error as e:
        conn.rollback() # Roll back changes if any error occurs
        print(f"Database error during order edit: {e}")
        return jsonify({"error": "Failed to update order due to a database error"}), 500
    finally:
        if conn:
            conn.close()

@app.route("/orders/<int:order_id>/logs", methods=["GET"])
def get_order_logs(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT action, timestamp FROM order_logs WHERE order_id = ? ORDER BY timestamp ASC", (order_id,))
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(logs)

# ---------- PRODUCTS API ENDPOINTS (Unchanged, but included for completeness) ----------
# In app.py

@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # --- START NEW SEARCH LOGIC ---
    search_query = request.args.get('search', '')
    
    if search_query:
        query = "SELECT * FROM products WHERE name LIKE ? OR sku LIKE ? ORDER BY product_id DESC"
        params = (f'%{search_query}%', f'%{search_query}%')
        cursor.execute(query, params)
    else:
        query = "SELECT * FROM products ORDER BY product_id DESC"
        cursor.execute(query)
    # --- END NEW SEARCH LOGIC ---

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
    name, category, price, quantity, min_quantity = data.get("name"), data.get("category"), data.get("price"), data.get("quantity"), data.get("min_quantity")
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
        except (ValueError, IndexError):
            last_number = 0
        next_number = last_number + 1
    else:
        next_number = 1
    
    sku = f"{prefix}{next_number:03d}"
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO products (name, category, price, quantity, min_quantity, sku, creation_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, category, price, quantity, min_quantity, sku, timestamp))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product added successfully", "sku": sku}), 201

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    name = data.get("name")
    category = data.get("category")
    price = data.get("price")
    new_quantity = data.get("quantity")
    min_quantity = data.get("min_quantity")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve old quantity
    cursor.execute("SELECT quantity FROM products WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    old_quantity = row["quantity"]
    quantity_change = new_quantity - old_quantity

    # Update the product
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, price = ?, quantity = ?, min_quantity = ?, last_updated_timestamp = ?
        WHERE product_id = ?
    """, (name, category, price, new_quantity, min_quantity, timestamp, product_id))

    # Log quantity change if needed
    if quantity_change != 0:
        cursor.execute("""
            INSERT INTO product_logs (product_id, action, quantity_change, timestamp)
            VALUES (?, ?, ?, ?)
        """, (product_id, "Manual Update", quantity_change, timestamp))

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

@app.route("/products/<int:product_id>/logs", methods=["GET"])
def get_product_logs(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT action, quantity_change, timestamp
        FROM product_logs
        WHERE product_id = ?
        ORDER BY timestamp DESC
    """, (product_id,))
    logs = cursor.fetchall()
    conn.close()

    return jsonify([{
        "action": log["action"],
        "quantity_change": log["quantity_change"],
        "timestamp": log["timestamp"]
    } for log in logs])

from flask import send_file
import pandas as pd
import io

@app.route("/export_orders", methods=["GET"])
def export_orders():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            o.order_id,
            o.date,
            o.status,
            o.total,
            o.creation_timestamp,
            o.last_updated_timestamp,
            c.name AS customer_name,
            c.id_number,
            c.phone,
            c.email,
            c.street,
            c.city,
            c.postal_code,
            p.name AS product_name,
            p.sku,
            oi.quantity AS product_quantity
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        ORDER BY o.order_id
    """)

    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=[
        "Order ID", "Order Date", "Status", "Total", "Created At", "Last Updated",
        "Customer Name", "ID Number", "Phone", "Email", "Street", "City", "Postal Code",
        "Product Name", "SKU", "Product Quantity"
    ])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Orders")

        workbook = writer.book
        worksheet = writer.sheets["Orders"]

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9D9D9',
            'border': 1
        })

        for col_num, column_name in enumerate(df.columns):
            worksheet.write(0, col_num, column_name, header_format)
            column_width = max(df[column_name].astype(str).map(len).max(), len(column_name)) + 2
            worksheet.set_column(col_num, col_num, column_width)

        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="orders_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
@app.route('/export_inventory')
def export_inventory():
    conn = sqlite3.connect('doubleaction.db')
    cursor = conn.cursor()

    # Fetch products
    cursor.execute('''
        SELECT 
            product_id,
            sku,
            name,
            category,
            price,
            quantity,
            min_quantity,
            creation_timestamp,
            last_updated_timestamp,
            last_ordered_timestamp
        FROM products
        ORDER BY datetime(creation_timestamp) DESC
    ''')
    products_data = cursor.fetchall()
    product_columns = [desc[0] for desc in cursor.description]
    df_products = pd.DataFrame(products_data, columns=product_columns)

    # Fetch logs
    cursor.execute('''
        SELECT 
            pl.log_id,
            pl.product_id,
            p.name AS product_name,
            pl.action,
            pl.quantity_change,
            pl.timestamp
        FROM product_logs pl
        JOIN products p ON pl.product_id = p.product_id
        ORDER BY datetime(pl.timestamp) DESC
    ''')
    logs_data = cursor.fetchall()
    log_columns = [desc[0] for desc in cursor.description]
    df_logs = pd.DataFrame(logs_data, columns=log_columns)

    conn.close()

    # Write to Excel with formatting
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Inventory sheet
        df_products.to_excel(writer, index=False, sheet_name='Inventory')
        workbook  = writer.book
        sheet1 = writer.sheets['Inventory']

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9D9D9',
            'border': 1
        })

        for col_num, value in enumerate(df_products.columns.values):
            sheet1.write(0, col_num, value, header_format)
            column_width = max(df_products[value].astype(str).map(len).max(), len(value)) + 2
            sheet1.set_column(col_num, col_num, column_width)

        sheet1.autofilter(0, 0, len(df_products), len(df_products.columns) - 1)

        # Logs sheet
        df_logs.to_excel(writer, index=False, sheet_name='Logs')
        sheet2 = writer.sheets['Logs']

        for col_num, value in enumerate(df_logs.columns.values):
            sheet2.write(0, col_num, value, header_format)
            column_width = max(df_logs[value].astype(str).map(len).max(), len(value)) + 2
            sheet2.set_column(col_num, col_num, column_width)

        sheet2.autofilter(0, 0, len(df_logs), len(df_logs.columns) - 1)

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="inventory_export.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
# ---------- MAIN EXECUTION ----------

if __name__ == "__main__":
    app.run(debug=True)
