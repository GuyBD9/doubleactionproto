# seed_database.py (VERSION 3 - FINAL)
# This version includes the user's FULL product list and seeds customers and orders.

import sqlite3
import random
import datetime
import os

# --- CONFIGURATION ---
DB_PATH = "doubleaction.db"
NUM_CUSTOMERS = 15
NUM_ORDERS = 40  # Increased to 40 for more data

# A list of realistic products for the store (USER'S FULL LIST)
PRODUCTS_DATA = {
    "Jackets": [
        {"name": "Slim-Fit Wool Blazer - Charcoal Grey", "price_range": (1200, 1800)},
        {"name": "Classic Navy Blue Tuxedo Jacket", "price_range": (1500, 2200)},
        {"name": "Linen Blend Summer Jacket - Beige", "price_range": (900, 1400)},
        {"name": "Double-Breasted Pinstripe Jacket", "price_range": (1300, 1900)},
        {"name": "Velvet Evening Jacket - Burgundy", "price_range": (1600, 2500)},
        {"name": "Modern Tweed Sport Coat", "price_range": (1100, 1700)},
        {"name": "Lightweight Travel Blazer - Olive", "price_range": (800, 1300)},
        {"name": "Peak Lapel Dinner Jacket - Ivory", "price_range": (1700, 2600)},
        {"name": "Checkered Wool Jacket - Brown", "price_range": (1250, 1850)},
        {"name": "Structured Cotton Blazer - Royal Blue", "price_range": (950, 1500)},
    ],
    "Pants": [
        {"name": "Tailored Wool Trousers - Black", "price_range": (450, 700)},
        {"name": "Slim-Fit Chinos - Khaki", "price_range": (350, 600)},
        {"name": "Formal Pinstripe Dress Pants", "price_range": (500, 750)},
        {"name": "Linen Drawstring Trousers - White", "price_range": (400, 650)},
        {"name": "Modern Fit Flat-Front Pants - Grey", "price_range": (450, 700)},
        {"name": "Tuxedo Pants with Satin Stripe", "price_range": (600, 900)},
        {"name": "Stretch Cotton Trousers - Navy", "price_range": (400, 650)},
        {"name": "High-Waisted Gurkha Trousers", "price_range": (550, 800)},
        {"name": "Checkered Dress Slacks", "price_range": (500, 750)},
        {"name": "Corduroy Trousers - Forest Green", "price_range": (450, 700)},
    ],
    "Shirts": [
        {"name": "Crisp White Cotton Dress Shirt", "price_range": (300, 500)},
        {"name": "Light Blue Oxford Button-Down", "price_range": (280, 480)},
        {"name": "Formal French Cuff Tuxedo Shirt", "price_range": (400, 650)},
        {"name": "Silk Blend Evening Shirt - Black", "price_range": (500, 800)},
        {"name": "Patterned Floral Print Shirt", "price_range": (320, 550)},
        {"name": "Mandarin Collar Linen Shirt - Sky Blue", "price_range": (350, 580)},
        {"name": "Non-Iron Twill Dress Shirt - Pink", "price_range": (300, 500)},
        {"name": "Classic Gingham Check Shirt", "price_range": (280, 480)},
        {"name": "Denim Effect Casual Shirt", "price_range": (300, 520)},
        {"name": "Striped Business Shirt - Grey/White", "price_range": (290, 490)},
    ],
    "Vests": [
        {"name": "Classic 5-Button Suit Vest - Grey", "price_range": (350, 550)},
        {"name": "Double-Breasted Tweed Waistcoat", "price_range": (450, 700)},
        {"name": "Low-Cut Formal Tuxedo Vest", "price_range": (400, 600)},
        {"name": "Satin Back Wedding Vest - Silver", "price_range": (380, 580)},
        {"name": "Linen-Blend Casual Vest - Natural", "price_range": (300, 500)},
        {"name": "Checkered Wool Waistcoat", "price_range": (420, 650)},
        {"name": "Knit-Effect Sweater Vest", "price_range": (280, 480)},
        {"name": "Horseshoe U-Shaped Formal Vest", "price_range": (450, 680)},
        {"name": "Quilted Puffer Vest - Navy", "price_range": (350, 600)},
        {"name": "Suede-Front Casual Vest - Tan", "price_range": (500, 750)},
    ],
    "Ties": [
        {"name": "Italian Silk Tie - Navy Paisley", "price_range": (200, 350)},
        {"name": "Knitted Wool Tie - Charcoal", "price_range": (180, 320)},
        {"name": "Classic Striped Repp Tie", "price_range": (190, 330)},
        {"name": "Formal Satin Bow Tie - Black", "price_range": (150, 280)},
        {"name": "Linen Tie - Light Grey", "price_range": (170, 300)},
        {"name": "Floral Pattern Cotton Tie", "price_range": (180, 320)},
        {"name": "Cashmere Blend Tie - Burgundy", "price_range": (250, 400)},
        {"name": "Polka Dot Silk Tie - Blue/White", "price_range": (200, 350)},
        {"name": "Plaid Flannel Winter Tie", "price_range": (190, 340)},
        {"name": "Velvet Pre-Tied Bow Tie", "price_range": (160, 290)},
    ],
    "Fabrics": [
        {"name": "Italian Super 120s Wool - Navy", "price_range": (300, 500)},
        {"name": "English Tweed - Herringbone", "price_range": (350, 550)},
        {"name": "Irish Linen - Natural White", "price_range": (250, 450)},
        {"name": "Cashmere-Wool Blend - Heather Grey", "price_range": (450, 700)},
        {"name": "Silk and Cotton Blend - Lurex", "price_range": (400, 650)},
        {"name": "Pima Cotton Twill - Khaki", "price_range": (200, 350)},
        {"name": "Velvet - Deep Emerald Green", "price_range": (380, 600)},
        {"name": "Seersucker Cotton - Blue/White Stripe", "price_range": (220, 400)},
        {"name": "Flannel Wool - Charcoal", "price_range": (320, 520)},
        {"name": "Merino Wool Jersey Knit - Black", "price_range": (280, 480)},
    ]
}

SKU_PREFIXES = {
    "Fabrics": "FAB", "Pants": "PNT", "Vests": "VST",
    "Jackets": "JCK", "Shirts": "SHT", "Ties": "TIE"
}

def setup_database():
    """Deletes the old DB and creates a new one from the setup script."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database '{DB_PATH}'.")
    
    import database_setup
    print("Database schema created successfully.")

def seed_products(cursor):
    """Populates the products table with the full list of sample data."""
    print("\n--- Seeding Products ---")
    total_items_added = 0
    for category, items in PRODUCTS_DATA.items():
        prefix = SKU_PREFIXES.get(category, "GEN")
        for i, item_data in enumerate(items, 1):
            name = item_data["name"]
            price = round(random.uniform(*item_data["price_range"]), 2)
            quantity = random.randint(20, 100) # Start with higher stock
            min_quantity = random.choice([5, 10, 15])
            sku = f"{prefix}{i:03d}"
            timestamp = (datetime.datetime.now() - datetime.timedelta(days=random.randint(200, 365))).strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO products (sku, name, category, price, quantity, min_quantity, creation_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sku, name, category, price, quantity, min_quantity, timestamp))
            total_items_added += 1
    print(f"Added {total_items_added} products.")

def seed_customers(cursor):
    """Populates the customers table with sample data."""
    print("\n--- Seeding Customers ---")
    customers = [
        {"name": "Avi Cohen", "id_number": "123456789", "phone": "050-1234567", "email": "avi.c@email.com", "street": "Herzl 1", "city": "Tel Aviv", "postal_code": "61000"},
        {"name": "Yossi Levi", "id_number": "234567890", "phone": "052-2345678", "email": "yossi.l@email.com", "street": "Bialik 2", "city": "Ramat Gan", "postal_code": "52000"},
        {"name": "Moshe Mizrahi", "id_number": "345678901", "phone": "054-3456789", "email": "moshe.m@email.com", "street": "Weizmann 3", "city": "Givatayim", "postal_code": "53000"},
        {"name": "Dana Shalom", "id_number": "456789012", "phone": "053-4567890", "email": "dana.s@email.com", "street": "Rothschild 4", "city": "Tel Aviv", "postal_code": "65000"},
        {"name": "Gal Gadot", "id_number": "987654321", "phone": "058-9876543", "email": "gal.g@email.com", "street": "Dizengoff 100", "city": "Tel Aviv", "postal_code": "64000"},
        {"name": "Idan Raichel", "id_number": "567890123", "phone": "055-5678901", "email": "idan.r@email.com", "street": "Hahagana 5", "city": "Kfar Saba", "postal_code": "44100"},
        {"name": "Shiri Maimon", "id_number": "678901234", "phone": "056-6789012", "email": "shiri.m@email.com", "street": "Jabotinsky 6", "city": "Rishon LeZion", "postal_code": "75000"},
        {"name": "Lior Suchard", "id_number": "789012345", "phone": "057-7890123", "email": "lior.s@email.com", "street": "Ahad Ha'am 7", "city": "Herzliya", "postal_code": "46100"}
    ]
    for cust in customers:
        cursor.execute("""
            INSERT INTO customers (name, id_number, phone, email, street, city, postal_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cust["name"], cust["id_number"], cust["phone"], cust["email"], cust["street"], cust["city"], cust["postal_code"]))
    print(f"Added {len(customers)} customers.")

def seed_orders(cursor):
    """Creates random orders for existing customers with existing products."""
    print("\n--- Seeding Orders ---")
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id, price FROM products")
    products = [{"id": row[0], "price": row[1]} for row in cursor.fetchall()]

    if not customer_ids or not products:
        print("Cannot seed orders without customers and products.")
        return

    for i in range(NUM_ORDERS):
        customer_id = random.choice(customer_ids)
        days_ago = random.randint(1, 180)
        order_date = datetime.date.today() - datetime.timedelta(days=days_ago)
        timestamp = (datetime.datetime.now() - datetime.timedelta(days=days_ago, hours=random.randint(1,23))).strftime("%Y-%m-%d %H:%M:%S")
        status = random.choice(["Delivered", "Shipped", "Pending", "Order Received", "Cancelled"])
        
        order_items = []
        order_total = 0
        num_items_in_order = random.randint(1, 4)
        chosen_products = random.sample(products, num_items_in_order)
        
        for product in chosen_products:
            quantity = random.randint(1, 3)
            order_items.append({"product_id": product["id"], "quantity": quantity})
            order_total += product["price"] * quantity

        cursor.execute("""
            INSERT INTO orders (customer_id, date, status, total, creation_timestamp, last_updated_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (customer_id, order_date.isoformat(), status, round(order_total, 2), timestamp, timestamp))
        order_id = cursor.lastrowid
        cursor.execute("INSERT INTO order_logs (order_id, action, timestamp) VALUES (?, ?, ?)", 
                       (order_id, "Order created (Seed)", timestamp))

        for item in order_items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                           (order_id, product_id, quantity))
            
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
                           (quantity, product_id))
            
            # Log inventory and last ordered timestamp
            cursor.execute("UPDATE products SET last_ordered_timestamp = ? WHERE product_id = ?", (timestamp, product_id))
            cursor.execute("""
                INSERT INTO product_logs (product_id, action, quantity_change, timestamp)
                VALUES (?, ?, ?, ?)
            """, (product_id, f"Sale (Order #{order_id})", -quantity, timestamp))

    print(f"Added {NUM_ORDERS} orders.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        setup_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        seed_products(cursor)
        seed_customers(cursor)
        seed_orders(cursor)
        
        conn.commit()
        print("\nDatabase seeding complete with FULL product list!")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")