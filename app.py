import os
import random
import requests
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'oms_store_master_key_2026'

# ==========================================
# CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN = "8988154095:AAHIoRgwHA08Mfw1viZFUPdeUpJyjF3dRTI"
TELEGRAM_CHAT_ID = "7867296083"

# ==========================================
# TELEGRAM NOTIFICATION HELPER
# ==========================================
def send_telegram_notification(title, details):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{title}\n\n{details}",
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload)
        print("Telegram Response:", res.status_code, res.text)
    except Exception as e:
        print("Telegram Error:", e)

# ==========================================
# DATA & PRODUCTS
# ==========================================
PRODUCTS = [
    {
        "id": 1,
        "name": "Sony WH-1000XM5 Wireless Headphones",
        "category": "Audio",
        "price": 24999.00,
        "mrp": 29999.00,
        "discount": "16% OFF",
        "rating": 4.8,
        "reviews": 1240,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
        "tag": "Bestseller",
        "delivery": "FREE Delivery by Tomorrow",
        "description": "Industry-leading noise canceling with two processors and 8 microphones for crystal clear audio quality."
    },
    {
        "id": 2,
        "name": "Apple Watch Series 9 GPS 45mm",
        "category": "Wearables",
        "price": 32900.00,
        "mrp": 38900.00,
        "discount": "15% OFF",
        "rating": 4.9,
        "reviews": 850,
        "image": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=500&q=80",
        "tag": "Trending",
        "delivery": "FREE Delivery within 2 Days",
        "description": "Powerful sensors, advanced health monitoring features, and a much brighter Always-On Retina display."
    },
    {
        "id": 3,
        "name": "Logitech MX Master 3S Wireless Mouse",
        "category": "Accessories",
        "price": 8499.00,
        "mrp": 9999.00,
        "discount": "15% OFF",
        "rating": 4.7,
        "reviews": 2100,
        "image": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&q=80",
        "tag": "Top Rated",
        "delivery": "FREE Express Delivery",
        "description": "An iconic mouse remastered for ultimate tactility, performance, and flow with 8K DPI tracking on any surface."
    },
    {
        "id": 4,
        "name": "JBL Flip 6 Portable Bluetooth Speaker",
        "category": "Audio",
        "price": 6999.00,
        "mrp": 9999.00,
        "discount": "30% OFF",
        "rating": 4.6,
        "reviews": 540,
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500&q=80",
        "tag": "Hot Deal",
        "delivery": "FREE Delivery by Tomorrow",
        "description": "Bold sound for every adventure. Waterproof design paired with crisp high-output acoustic configuration."
    }
]

# ==========================================
# HTML TEMPLATES WITH APP-STYLE BOTTOM NAV
# ==========================================
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Om's Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin:0; padding-bottom: 70px; background:#f1f2f6; color:#333; }
        
        /* App-Style Header */
        header { background: #111; color: #fff; padding: 12px 16px; display: flex; flex-direction: column; gap: 10px; position: sticky; top: 0; z-index: 100; box-shadow:0 2px 8px rgba(0,0,0,0.2); }
        .top-row { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 18px; font-weight: 800; display: flex; align-items: center; gap: 6px; }
        .logo span { background: #ff4757; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 900; }
        .cart-icon { position: relative; color: white; text-decoration: none; font-size: 20px; }
        .cart-badge { position: absolute; top: -6px; right: -10px; background: #ff4757; color: white; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 10px; }

        /* Search Bar */
        .search-box { display: flex; width: 100%; }
        .search-box input { width: 100%; padding: 10px 14px; border: none; border-radius: 8px 0 0 8px; font-size: 13px; outline: none; }
        .search-box button { background: #ff4757; color: white; border: none; padding: 10px 14px; border-radius: 0 8px 8px 0; cursor: pointer; font-weight: bold; }

        /* Category Bar */
        .cat-bar { display: flex; gap: 8px; padding: 10px 14px; overflow-x: auto; background: #fff; border-bottom: 1px solid #e1e2e6; }
        .cat-btn { background: #f1f2f6; color: #222; padding: 6px 14px; border-radius: 20px; text-decoration: none; font-size: 12px; font-weight: 600; white-space: nowrap; }
        .cat-btn.active { background: #111; color: #fff; }

        /* Product Grid */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; max-width: 800px; margin: auto; }
        .card { background: #fff; border-radius: 10px; padding: 10px; position: relative; box-shadow: 0 2px 5px rgba(0,0,0,0.04); display: flex; flex-direction: column; justify-content: space-between; }
        .badge { position: absolute; top: 10px; left: 10px; background: gold; color: #000; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; z-index: 1; }
        .card img { width: 100%; height: 120px; object-fit: cover; border-radius: 6px; }
        .title { font-size: 13px; font-weight: 600; margin: 6px 0 3px; height: 32px; overflow: hidden; text-decoration: none; color: #222; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .rating { color: #ffa500; font-size: 11px; margin-bottom: 3px; }
        .price { font-size: 14px; font-weight: bold; color: #d63031; margin: 2px 0; }
        .mrp { font-size: 10px; color: #888; text-decoration: line-through; }
        .disc { font-size: 11px; color: green; font-weight: bold; }
        .del-info { font-size: 10px; color: #27ae60; font-weight: 600; margin: 4px 0 8px; }
        .btn { display: block; width: 100%; background: #e17055; color: white; text-align: center; padding: 9px 0; border: none; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 12px; cursor: pointer; margin-top: auto; }

        /* FIXED Flipkart/Amazon Style Bottom Navigation Bar */
        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-around; padding: 8px 0; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); z-index: 1000; }
        .nav-item { display: flex; flex-direction: column; align-items: center; text-decoration: none; color: #718096; font-size: 10px; font-weight: 600; }
        .nav-item.active { color: #ff4757; }
        .nav-item span { font-size: 18px; margin-bottom: 2px; }

        /* Modern Toast */
        .toast-container { position: fixed; top: 70px; right: 20px; z-index: 9999; }
        .toast { background: rgba(46, 213, 115, 0.95); backdrop-filter: blur(10px); color: white; padding: 12px 20px; border-radius: 8px; font-size: 13px; font-weight: 600; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); }
    </style>
</head>
<body>
    <div class="toast-container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">✨ {{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    </div>

    <header>
        <div class="top-row">
            <div class="logo">Om's Store <span>Plus</span></div>
            <a href="/cart" class="cart-icon">🛒 <span class="cart-badge">{{ cart_count }}</span></a>
        </div>
        <form action="/" method="GET" class="search-box">
            <input type="text" name="q" placeholder="Search for products, brands..." value="{{ request.args.get('q', '') }}">
            <button type="submit">🔍</button>
        </form>
    </header>

    <div class="cat-bar">
        <a href="/" class="cat-btn active">All Categories</a>
        <a href="/?cat=Audio" class="cat-btn">Audio</a>
        <a href="/?cat=Wearables" class="cat-btn">Wearables</a>
        <a href="/?cat=Accessories" class="cat-btn">Accessories</a>
    </div>

    <div class="grid">
        {% for p in products %}
        <div class="card">
            <span class="badge">{{ p.tag }}</span>
            <a href="/product/{{ p.id }}"><img src="{{ p.image }}"></a>
            <a href="/product/{{ p.id }}" class="title">{{ p.name }}</a>
            <div class="rating">★ {{ p.rating }} <span style="color:#888;">({{ p.reviews }})</span></div>
            <div class="price">₹{{ p.price }} <span class="mrp">₹{{ p.mrp }}</span></div>
            <div class="disc">{{ p.discount }}</div>
            <div class="del-info">🚚 {{ p.delivery }}</div>
            <a href="/add_to_cart/{{ p.id }}" class="btn">ADD TO CART</a>
        </div>
        {% endfor %}
    </div>

    <!-- App Bottom Nav Bar -->
    <nav class="bottom-nav">
        <a href="/" class="nav-item active"><span>🏠</span>Home</a>
        <a href="/cart" class="nav-item"><span>🛒</span>Cart</a>
        <a href="/orders" class="nav-item"><span>📦</span>Orders</a>
        {% if user %}
            <a href="/logout" class="nav-item"><span>👤</span>Logout</a>
        {% else %}
            <a href="/login" class="nav-item"><span>🔑</span>Account</a>
        {% endif %}
    </nav>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>OTP Verification - Om's Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#f1f2f6; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }
        .card { background:white; padding:25px; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.08); width:300px; text-align:center; }
        input { width:100%; padding:12px; margin:10px 0; border:1px solid #ccc; border-radius:8px; box-sizing:border-box; font-size:14px; }
        .btn { width:100%; background:#111; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:10px; font-size:14px; }
        .back { text-decoration:none; color:#555; font-size:12px; display:block; margin-bottom:15px; text-align:left; }
        
        /* Modern Toast for OTP display */
        .toast-container { position: fixed; top: 20px; right: 20px; left: 20px; display: flex; justify-content: center; z-index: 9999; pointer-events: none; }
        .toast { background: rgba(46, 213, 115, 0.95); backdrop-filter: blur(10px); color: white; padding: 15px 25px; border-radius: 8px; font-size: 16px; font-weight: bold; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); animation: slideDown 0.4s ease forwards; pointer-events: auto; }
        @keyframes slideDown { from { transform: translateY(-50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    </style>
</head>
<body>
    <!-- THIS IS WHERE THE OTP WILL POP UP -->
    <div class="toast-container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">🔔 {{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    </div>

    <div class="card">
        <a href="/" class="back">← Back to Store</a>
        <h2 style="margin-bottom:5px;">OTP Login</h2>
        <p style="font-size:12px; color:#666; margin-bottom:20px;">Enter your Mobile Number or Email to receive an OTP</p>

        {% if not otp_sent %}
        <form action="/send_otp" method="POST">
            <input type="text" name="identifier" placeholder="Mobile No or Email ID" required><br>
            <button type="submit" class="btn">SEND OTP</button>
        </form>
        {% else %}
        <form action="/verify_otp" method="POST">
            <input type="text" name="otp_input" placeholder="Enter 4-Digit OTP" maxlength="4" required style="letter-spacing: 5px; text-align:center; font-weight:bold; font-size:18px;"><br>
            <button type="submit" class="btn" style="background:#27ae60;">VERIFY & LOGIN</button>
        </form>
        {% endif %}
    </div>
</body>
</html>
"""


CART_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Your Cart & Checkout</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding:15px; padding-bottom:70px; background:#f4f4f4; max-width:600px; margin:auto; }
        .box { background:white; padding:18px; border-radius:12px; margin-bottom:15px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
        .cart-item { display:flex; align-items:center; gap:12px; padding:12px 0; border-bottom:1px solid #eee; }
        .cart-item img { width:60px; height:60px; object-fit:cover; border-radius:8px; }
        .item-info { flex:1; }
        .item-title { font-size:13px; font-weight:bold; color:#222; margin-bottom:4px; }
        .item-price { font-size:14px; font-weight:bold; color:#d63031; }
        
        .qty-controls { display:flex; align-items:center; gap:8px; margin-top:6px; }
        .qty-btn { background:#f1f2f6; border:1px solid #ccc; width:26px; height:26px; border-radius:5px; display:flex; justify-content:center; align-items:center; font-weight:bold; text-decoration:none; color:#333; font-size:14px; }
        .qty-val { font-size:13px; font-weight:bold; min-width:18px; text-align:center; }
        .delete-btn { color:#e74c3c; text-decoration:none; font-size:16px; margin-left:auto; padding:4px; }

        .pay-option { background:#f8f9fa; border:1px solid #e2e8f0; padding:12px; border-radius:8px; margin:8px 0; font-size:14px; cursor:pointer; }
        .pay-fields { display:none; padding:10px 0 0 0; }
        .pay-fields input { width:100%; padding:9px; margin:5px 0; border:1px solid #ccc; border-radius:6px; font-size:13px; }
        .btn { background:#27ae60; color:white; padding:14px; text-align:center; display:block; border-radius:8px; border:none; width:100%; font-size:16px; font-weight:bold; cursor:pointer; margin-top:10px; }
        .back { color:#333; text-decoration:none; display:inline-block; margin-bottom:12px; font-weight:bold; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-around; padding: 8px 0; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); z-index: 1000; }
        .nav-item { display: flex; flex-direction: column; align-items: center; text-decoration: none; color: #718096; font-size: 10px; font-weight: 600; }
        .nav-item.active { color: #ff4757; }
        .nav-item span { font-size: 18px; margin-bottom: 2px; }
    </style>
</head>
<body>
    <a href="/" class="back">← Back to Shop</a>
    <h2>Shopping Cart</h2>
    {% if cart %}
        <div class="box">
            {% for p_id, item in cart.items() %}
            <div class="cart-item">
                <img src="{{ item.image }}">
                <div class="item-info">
                    <div class="item-title">{{ item.name }}</div>
                    <div class="item-price">₹{{ item.price }}</div>
                    <div class="qty-controls">
                        <a href="/update_qty/{{ p_id }}/dec" class="qty-btn">-</a>
                        <span class="qty-val">{{ item.qty }}</span>
                        <a href="/update_qty/{{ p_id }}/inc" class="qty-btn">+</a>
                    </div>
                </div>
                <a href="/remove_item/{{ p_id }}" class="delete-btn">🗑️</a>
            </div>
            {% endfor %}
            
            <div style="display:flex; justify-content:space-between; margin-top:15px; font-size:16px; font-weight:bold;">
                <span>Total Amount:</span>
                <span style="color:#d63031;">₹{{ total }}</span>
            </div>
        </div>

        <div class="box">
            <h3>Payment Method</h3>
            <form action="/checkout" method="POST">
                <div class="pay-option" onclick="selectPay('upi')">
                    <input type="radio" id="radio_upi" name="payment_method" value="UPI / Online" checked> 📱 <b>UPI Payment</b>
                    <div id="fields_upi" class="pay-fields" style="display:block;">
                        <input type="text" name="upi_id" placeholder="Enter UPI ID (e.g. name@upi)" required>
                    </div>
                </div>

                <div class="pay-option" onclick="selectPay('card')">
                    <input type="radio" id="radio_card" name="payment_method" value="Credit/Debit Card"> 💳 <b>Credit / Debit Card</b>
                    <div id="fields_card" class="pay-fields">
                        <input type="text" name="card_number" placeholder="16-digit Card Number">
                        <div style="display:flex; gap:8px;">
                            <input type="text" name="card_exp" placeholder="MM/YY">
                            <input type="password" name="card_cvv" placeholder="CVV">
                        </div>
                    </div>
                </div>

                <div class="pay-option" onclick="selectPay('cod')">
                    <input type="radio" id="radio_cod" name="payment_method" value="Cash on Delivery"> 💵 <b>Cash on Delivery (COD)</b>
                </div>

                <p style="font-size:12px; color:#666; margin-top:15px; line-height:1.4;">
                    <b>Shipping Address:</b><br>
                    Haider enclave, house no. 87 Ladian near, livguard battery factory
                </p>

                <button type="submit" class="btn">PLACE ORDER (₹{{ total }})</button>
            </form>
        </div>
    {% else %}
        <div class="box" style="text-align:center; padding:30px;">
            <p style="font-size:16px; color:#666;">Your cart is empty!</p>
            <a href="/" style="background:#111; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; display:inline-block; font-weight:bold;">Start Shopping</a>
        </div>
    {% endif %}

    <nav class="bottom-nav">
        <a href="/" class="nav-item"><span>🏠</span>Home</a>
        <a href="/cart" class="nav-item active"><span>🛒</span>Cart</a>
        <a href="/orders" class="nav-item"><span>📦</span>Orders</a>
        <a href="/login" class="nav-item"><span>👤</span>Account</a>
    </nav>

    <script>
        function selectPay(type) {
            document.getElementById('fields_upi').style.display = 'none';
            document.getElementById('fields_card').style.display = 'none';
            if (type === 'upi') {
                document.getElementById('radio_upi').checked = true;
                document.getElementById('fields_upi').style.display = 'block';
            } else if (type === 'card') {
                document.getElementById('radio_card').checked = true;
                document.getElementById('fields_card').style.display = 'block';
            } else {
                document.getElementById('radio_cod').checked = true;
            }
        }
    </script>
</body>
</html>
"""

ORDERS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Your Orders</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding:15px; padding-bottom:70px; background:#f4f4f4; max-width:600px; margin:auto; }
        .order-card { background:white; border-radius:12px; padding:18px; margin-bottom:15px; box-shadow:0 3px 10px rgba(0,0,0,0.05); }
        .order-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
        .badge { padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold; }
        .badge-active { background:#e8f8f0; color:#27ae60; }
        .badge-cancelled { background:#ffe0e0; color:#e74c3c; }
        .item-row { display:flex; justify-content:space-between; font-size:13px; margin:6px 0; color:#485460; }
        .total-row { display:flex; justify-content:space-between; font-weight:bold; font-size:15px; margin-top:12px; padding-top:10px; border-top:1px dashed #ddd; color:#d63031; }
        .action-row { display:flex; gap:10px; margin-top:15px; }
        .btn-action { flex:1; text-align:center; padding:9px; border-radius:6px; text-decoration:none; font-size:12px; font-weight:bold; color:white; }
        .btn-cancel { background:#ff4757; }
        .btn-return { background:#ffa502; }
        .back { color:#333; text-decoration:none; display:inline-block; margin-bottom:12px; font-weight:bold; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-around; padding: 8px 0; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); z-index: 1000; }
        .nav-item { display: flex; flex-direction: column; align-items: center; text-decoration: none; color: #718096; font-size: 10px; font-weight: 600; }
        .nav-item.active { color: #ff4757; }
        .nav-item span { font-size: 18px; margin-bottom: 2px; }
    </style>
</head>
<body>
    <a href="/" class="back">← Back to Shop</a>
    <h2>My Orders Dashboard</h2>
    {% if orders %}
        {% for o in orders %}
        <div class="order-card">
            <div class="order-header">
                <div>
                    <b>Order #{{ loop.index }}</b><br>
                    <small style="color:#888;">{{ o['date'] }}</small>
                </div>
                {% if o['status'] == 'Cancelled' %}
                    <span class="badge badge-cancelled">Cancelled</span>
                {% else %}
                    <span class="badge badge-active">Out for Delivery</span>
                {% endif %}
            </div>

            <div style="margin:10px 0;">
                {% for item in o['order_items'] %}
                <div class="item-row">
                    <span>• <b>{{ item['name'] }}</b> x{{ item['qty'] }}</span>
                    <span>₹{{ item['price'] * item['qty'] }}</span>
                </div>
                {% endfor %}
            </div>

            <div class="total-row">
                <span>Total Paid</span>
                <span>₹{{ o['total'] }}</span>
            </div>

            {% if o['status'] == 'Active' %}
            <div class="action-row">
                <a href="/cancel_order/{{ loop.index0 }}" class="btn-action btn-cancel">Cancel Order</a>
                <a href="/return_order/{{ loop.index0 }}" class="btn-action btn-return">Return Order</a>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <div class="order-card" style="text-align:center; padding:30px;">
            <p style="color:#666;">No orders placed yet!</p>
        </div>
    {% endif %}

    <nav class="bottom-nav">
        <a href="/" class="nav-item"><span>🏠</span>Home</a>
        <a href="/cart" class="nav-item"><span>🛒</span>Cart</a>
        <a href="/orders" class="nav-item active"><span>📦</span>Orders</a>
        <a href="/login" class="nav-item"><span>👤</span>Account</a>
    </nav>
</body>
</html>
"""

# ==========================================
# ROUTES & LOGIC WITH OTP SYSTEM
# ==========================================
@app.route('/')
def home():
    cat = request.args.get('cat')
    search_query = request.args.get('q', '').strip().lower()
    
    filtered_products = PRODUCTS
    if cat:
        filtered_products = [p for p in filtered_products if p['category'] == cat]
    if search_query:
        filtered_products = [p for p in filtered_products if search_query in p['name'].lower() or search_query in p['category'].lower()]
    
    # Safe Cart Check: Reset old list session to dictionary if needed
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
        session['cart'] = cart

    cart_count = sum(item['qty'] for item in cart.values())
    user = session.get('user')
    return render_template_string(HOME_HTML, products=filtered_products, cart_count=cart_count, user=user)


@app.route('/login')
def login():
    return render_template_string(LOGIN_HTML, otp_sent=False)

@app.route('/send_otp', methods=['POST'])
def send_otp():
    identifier = request.form.get('identifier', '').strip()
    
    # 1. Check if input is empty
    if not identifier:
        flash("Please enter a valid Mobile Number or Email!")
        return render_template_string(LOGIN_HTML, otp_sent=False)

    # 2. Basic validation check (must be 10 digits OR a valid email format)
    is_phone = identifier.isdigit() and len(identifier) == 10
    is_email = "@" in identifier and "." in identifier

    if not (is_phone or is_email):
        flash("Invalid format! Enter a 10-digit mobile number or valid email.")
        return render_template_string(LOGIN_HTML, otp_sent=False)

    # 3. Check against registered users (optional restriction)
    # If you want to allow ANY valid number/email to register/login, you can remove this block.
    registered_users = ["07973813354", "om@example.com", "9876543210"]
    if identifier not in registered_users:
        flash("Number/Email not registered! Please use a registered account.")
        return render_template_string(LOGIN_HTML, otp_sent=False)

    # If valid & registered -> Generate OTP
    otp = str(random.randint(1000, 9999))
    session['generated_otp'] = otp
    session['user_identifier'] = identifier
    flash(f"Your OTP is: {otp}")
    return render_template_string(LOGIN_HTML, otp_sent=True)


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form.get('otp_input')
    if user_otp == session.get('generated_otp'):
        session['user'] = {"name": session.get('user_identifier'), "phone": session.get('user_identifier')}
        flash("Logged in successfully!")
        return redirect(url_for('home'))
    else:
        flash("Invalid OTP! Try again.")
        return render_template_string(LOGIN_HTML, otp_sent=True)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!")
    return redirect(url_for('home'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', {})
        p_id_str = str(product_id)
        if p_id_str in cart:
            cart[p_id_str]['qty'] += 1
        else:
            cart[p_id_str] = {
                "id": product['id'],
                "name": product['name'],
                "price": product['price'],
                "image": product['image'],
                "qty": 1
            }
        session['cart'] = cart
        flash(f"{product['name']} added to cart!")
    return redirect(request.referrer or url_for('home'))

@app.route('/update_qty/<string:product_id>/<string:action>')
def update_qty(product_id, action):
    cart = session.get('cart', {})
    if product_id in cart:
        if action == 'inc':
            cart[product_id]['qty'] += 1
        elif action == 'dec':
            cart[product_id]['qty'] -= 1
            if cart[product_id]['qty'] <= 0:
                del cart[product_id]
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_item/<string:product_id>')
def remove_item(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        flash("Item removed from cart.")
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
        session['cart'] = cart
        
    total = sum(item['price'] * item['qty'] for item in cart.values())
    return render_template_string(CART_HTML, cart=cart, total=total)


    payment_method = request.form.get('payment_method', 'UPI / Online')
    upi_id = request.form.get('upi_id', '')
    total = sum(item['price'] * item['qty'] for item in cart.values())
    
    user = session.get('user', {"name": "Om Prakash", "phone": "07973813354"})
    order_items_list = list(cart.values())

    new_order = {
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "order_items": order_items_list,
        "total": total,
        "customer_name": user['name'],
        "customer_phone": user.get('phone', '07973813354'),
        "payment": payment_method,
        "upi_id": upi_id,
        "status": "Active",
        "address": "Haider enclave, house no. 87 Ladian near, livguard battery factory"
    }

    orders = session.get('orders', [])
    orders.append(new_order)
    session['orders'] = orders
    session['cart'] = {}

    items_summary = "\n".join([f"- {item['name']} x{item['qty']} (₹{item['price'] * item['qty']})" for item in order_items_list])
    
    details = (
        f"*Customer:* {new_order['customer_name']}\n"
        f"*Payment Method:* {payment_method}\n"
        f"*Total Paid:* ₹{total}\n\n"
        f"*Items:*\n{items_summary}\n\n"
        f"*Address:* {new_order['address']}"
    )
    
    send_telegram_notification("🛒 *New Order Received on Om's Store!*", details)

    return redirect(url_for('orders'))

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    orders = session.get('orders', [])
    if 0 <= order_id < len(orders):
        orders[order_id]['status'] = 'Cancelled'
        session['orders'] = orders
        
        o = orders[order_id]
        details = f"⚠️ *Order Cancelled*\n\n*Customer:* {o['customer_name']}\n*Amount:* ₹{o['total']}"
        send_telegram_notification("❌ *Order Cancellation Alert*", details)
        flash("Order cancelled successfully.")
    return redirect(url_for('orders'))

@app.route('/return_order/<int:order_id>')
def return_order(order_id):
    orders = session.get('orders', [])
    if 0 <= order_id < len(orders):
        orders[order_id]['status'] = 'Return Requested'
        session['orders'] = orders
        
        o = orders[order_id]
        details = f"🔄 *Return Requested*\n\n*Customer:* {o['customer_name']}\n*Amount:* ₹{o['total']}"
        send_telegram_notification("📦 *Return Request Alert*", details)
        flash("Return request submitted.")
    return redirect(url_for('orders'))

@app.route('/orders')
def orders():
    return render_template_string(ORDERS_HTML, orders=session.get('orders', []))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
