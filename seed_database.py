import sqlite3
import random
import datetime

DB_PATH = "doubleaction.db"

# A list of realistic products for the store
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

def seed_database():
    """
    Connects to the database and populates it with sample products.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print("Successfully connected to the database for seeding.")

        total_items_added = 0
        for category, items in PRODUCTS_DATA.items():
            print(f"\n--- Seeding category: {category} ---")
            
            prefix = SKU_PREFIXES.get(category, "GEN")
            cursor.execute("SELECT sku FROM products WHERE category = ? ORDER BY sku DESC LIMIT 1", (category,))
            last_sku = cursor.fetchone()
            
            start_number = 0
            if last_sku:
                try:
                    start_number = int(last_sku[0][-3:])
                except (ValueError, IndexError):
                    start_number = 0

            for i, item_data in enumerate(items, 1):
                name = item_data["name"]
                price = round(random.uniform(*item_data["price_range"]), 2)
                quantity = random.randint(3, 50) if random.random() > 0.1 else random.randint(1, 10)
                min_quantity = 10 if category != "Fabrics" else 5
                sku_number = start_number + i
                sku = f"{prefix}{sku_number:03d}"
                # ADDED: Get the current timestamp for each item
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    # UPDATED: Insert statement now includes the timestamp
                    cursor.execute("""
                        INSERT INTO products (sku, name, category, price, quantity, min_quantity, creation_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (sku, name, category, price, quantity, min_quantity, timestamp))
                    print(f"  Added: {name} (SKU: {sku})")
                    total_items_added += 1
                except sqlite3.IntegrityError:
                    print(f"  Skipped: SKU {sku} or item '{name}' likely already exists.")
        
        conn.commit()
        print(f"\nDatabase seeding complete. Total items added: {total_items_added}.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    seed_database()
