import os
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
def send_telegram_notification(order_details):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🛒 *New Order Received on Om's Store!*\n\n{order_details}",
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
USERS = {
    "om@example.com": {"name": "Om Prakash", "password": "password123", "phone": "07973813354"}
}

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
# HTML TEMPLATES
# ==========================================
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Om's Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; margin:0; background:#f4f4f4; color:#333; }
        header { background:#111; color:#fff; padding:12px; display:flex; flex-direction:column; gap:10px; }
        .top-row { display:flex; justify-content:space-between; align-items:center; }
        .logo { font-size:18px; font-weight:bold; }
        .logo span { background:red; padding:2px 6px; border-radius:3px; font-size:11px; }
        .search-box { display:flex; width:100%; }
        .search-box input { width:100%; padding:8px 12px; border:none; border-radius:4px 0 0 4px; font-size:14px; outline:none; }
        .search-box button { background:#e17055; color:white; border:none; padding:8px 14px; border-radius:0 4px 4px 0; cursor:pointer; font-weight:bold; }
        .nav-links { display:flex; gap:6px; }
        .nav-links a { color:#fff; text-decoration:none; background:#333; padding:5px 8px; border-radius:4px; font-size:12px; }
        .banner { background:#ff4757; color:white; text-align:center; padding:8px; font-size:12px; font-weight:bold; }
        .cat-bar { display:flex; gap:8px; padding:10px; overflow-x:auto; background:#fff; border-bottom:1px solid #ddd; }
        .cat-btn { background:#111; color:#fff; padding:6px 12px; border-radius:20px; text-decoration:none; font-size:12px; white-space:nowrap; }
        .grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; padding:10px; max-width:800px; margin:auto; }
        .card { background:#fff; border-radius:8px; padding:10px; position:relative; box-shadow:0 1px 3px rgba(0,0,0,0.1); display:flex; flex-direction:column; justify-space-between; }
        .badge { position:absolute; top:10px; left:10px; background:gold; color:#000; font-size:10px; font-weight:bold; padding:2px 5px; border-radius:3px; z-index:1; }
        .card img { width:100%; height:120px; object-fit:cover; border-radius:4px; cursor:pointer; }
        .title { font-size:13px; font-weight:bold; margin:6px 0 3px; height:32px; overflow:hidden; text-decoration:none; color:#333; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; }
        .title:hover { color:#e17055; }
        .rating { color:#ffa500; font-size:11px; margin-bottom:3px; }
        .price { font-size:14px; font-weight:bold; color:#d63031; margin:2px 0; }
        .mrp { font-size:10px; color:#888; text-decoration:line-through; }
        .disc { font-size:11px; color:green; font-weight:bold; }
        .del-info { font-size:10px; color:#27ae60; font-weight:bold; margin:4px 0 8px; }
        .btn { display:block; width:100%; background:#e17055; color:white; text-align:center; padding:8px 0; border:none; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px; cursor:pointer; margin-top:auto; }
        .toast { position: fixed; bottom: 20px; right: 20px; background: #2ed573; color: white; padding: 12px 20px; border-radius: 5px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.2); z-index: 1000; }
    </style>
</head>
<body>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">✅ {{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <header>
        <div class="top-row">
            <div class="logo">Om's Store <span>Plus</span></div>
            <div class="nav-links">
                {% if user %}
                    <a href="#">👤 {{ user.name }}</a>
                    <a href="/logout">Logout</a>
                {% else %}
                    <a href="/login">🔑 Login</a>
                {% endif %}
                <a href="/orders">📦 Orders</a>
                <a href="/cart">🛒 ({{ cart_count }})</a>
            </div>
        </div>
        <form action="/" method="GET" class="search-box">
            <input type="text" name="q" placeholder="Search products..." value="{{ request.args.get('q', '') }}">
            <button type="submit">🔍</button>
        </form>
    </header>

    <div class="banner">🏷️ FREE Express Delivery on all orders today!</div>

    <div class="cat-bar">
        <a href="/" class="cat-btn">All Items</a>
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

    <script>
        setTimeout(() => {
            let toast = document.querySelector('.toast');
            if(toast) toast.style.display = 'none';
        }, 3000);
    </script>
</body>
</html>
"""


PRODUCT_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ product.name }} - Om's Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background:#f4f4f4; margin:0; padding:15px; color:#333; }
        .container { max-width: 600px; margin: auto; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .back { color:#333; text-decoration:none; display:inline-block; margin-bottom:15px; font-weight:bold; }
        img { width: 100%; height: 250px; object-fit: cover; border-radius: 6px; }
        .title { font-size: 20px; font-weight: bold; margin: 15px 0 5px; }
        .price-section { font-size: 22px; font-weight: bold; color: #d63031; margin: 10px 0; }
        .mrp { font-size: 14px; color: #888; text-decoration: line-through; margin-left: 10px; }
        .desc { font-size: 14px; color: #555; line-height: 1.5; margin: 15px 0; }
        .del { background: #e8f8f0; color: #27ae60; padding: 10px; border-radius: 5px; font-weight: bold; margin-bottom: 15px; }
        .btn { background: #e17055; color: white; padding: 12px; text-align: center; display: block; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 16px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back">← Back to Store</a>
        <img src="{{ product.image }}">
        <div class="title">{{ product.name }}</div>
        <div class="rating">★ {{ product.rating }} ({{ product.reviews }} reviews)</div>
        <div class="price-section">₹{{ product.price }} <span class="mrp">₹{{ product.mrp }}</span> <span style="font-size:14px; color:green;">({{ product.discount }})</span></div>
        <div class="del">🚚 {{ product.delivery }}</div>
        <h3>Product Description</h3>
        <div class="desc">{{ product.description }}</div>
        <a href="/add_to_cart/{{ product.id }}" class="btn">ADD TO CART</a>
    </div>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Om's Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background:#f4f4f4; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }
        .card { background:white; padding:25px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1); width:280px; }
        input { width:92%; padding:10px; margin:8px 0; border:1px solid #ccc; border-radius:4px; }
        .btn { width:100%; background:#111; color:white; padding:10px; border:none; border-radius:4px; font-weight:bold; cursor:pointer; margin-top:10px; }
        .back { text-decoration:none; color:#555; font-size:12px; display:block; margin-bottom:15px; }
    </style>
</head>
<body>
    <div class="card">
        <a href="/" class="back">← Back to Store</a>
        <h2>Customer Login</h2>
        <form action="/login" method="POST">
            <input type="email" name="email" placeholder="Email (om@example.com)" required><br>
            <input type="password" name="password" placeholder="Password (password123)" required><br>
            <button type="submit" class="btn">LOGIN</button>
        </form>
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
        body { font-family: Arial, sans-serif; padding:15px; background:#f4f4f4; max-width:600px; margin:auto; }
        .box { background:white; padding:15px; border-radius:8px; margin-bottom:15px; box-shadow:0 1px 3px rgba(0,0,0,0.1); }
        .item { padding:8px 0; border-bottom:1px solid #eee; display:flex; justify-content:space-between; }
        .pay-option { background:#f9f9f9; border:1px solid #ddd; padding:10px; border-radius:5px; margin:8px 0; font-size:14px; }
        .btn { background:#27ae60; color:white; padding:12px; text-align:center; display:block; border-radius:5px; border:none; width:100%; font-size:16px; font-weight:bold; cursor:pointer; }
        .back { color:#333; text-decoration:none; display:inline-block; margin-bottom:10px; font-weight:bold; }
        .del-badge { background:#e8f8f0; color:#27ae60; padding:8px; border-radius:4px; font-size:12px; font-weight:bold; margin-bottom:10px; }
    </style>
</head>
<body>
    <a href="/" class="back">← Back to Shop</a>
    <h2>Cart & Payment Options</h2>
    {% if cart %}
        <div class="box">
            <div class="del-badge">🚚 FREE Express Delivery Eligible</div>
            <h3>Selected Items</h3>
            {% for item in cart %}
            <div class="item">
                <span><b>{{ item.name }}</b></span>
                <span>₹{{ item.price }}</span>
            </div>
            {% endfor %}
            <h3 style="color:#d63031; margin-top:15px;">Total Payable: ₹{{ total }}</h3>
        </div>

        <div class="box">
            <h3>Choose Payment Method</h3>
            <form action="/checkout" method="POST">
                <div class="pay-option">
                    <input type="radio" name="payment_method" value="UPI / Online" checked> 📱 <b>UPI / Online Payment</b>
                </div>
                <div class="pay-option">
                    <input type="radio" name="payment_method" value="Credit/Debit Card"> 💳 <b>Credit / Debit Card</b>
                </div>
                <div class="pay-option">
                    <input type="radio" name="payment_method" value="Cash on Delivery"> 💵 <b>Cash on Delivery (COD)</b>
                </div>

                <p style="font-size:12px; color:#666; margin-top:15px; line-height: 1.4;">
                    <b>Shipping Address:</b><br>
                    Haider enclave, house no. 87 Ladian near, livguard battery factory
                </p>

                <button type="submit" class="btn">CONFIRM ORDER (₹{{ total }})</button>
            </form>
        </div>
    {% else %}
        <div class="box"><p>Your cart is empty!</p></div>
    {% endif %}
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
        body { font-family: Arial, sans-serif; padding:15px; background:#f4f4f4; max-width:600px; margin:auto; }
        .order { background:white; padding:15px; border-radius:8px; margin-bottom:15px; box-shadow:0 2px 4px rgba(0,0,0,0.1); position:relative; }
        .status { color:green; background:#e8f8f0; padding:4px 10px; border-radius:4px; font-weight:bold; float:right; font-size:12px; }
        .status.cancelled { color:red; background:#ffe0e0; }
        .status.returned { color:#e67e22; background:#fff3e0; }
        .back { color:#333; text-decoration:none; display:inline-block; margin-bottom:10px; font-weight:bold; }
        .action-btn { padding:6px 12px; border:none; border-radius:4px; color:white; font-size:12px; font-weight:bold; cursor:pointer; text-decoration:none; display:inline-block; margin-top:10px; margin-right:5px; }
        .btn-cancel { background:#e74c3c; }
        .btn-return { background:#e67e22; }
    </style>
</head>
<body>
    <a href="/" class="back">← Back to Shop</a>
    <h2>Your Orders & Delivery Status</h2>
    {% if orders %}
        {% for o in orders %}
        <div class="order">
            {% if o['status'] == 'Cancelled' %}
                <span class="status cancelled">Cancelled</span>
            {% elif o['status'] == 'Return Requested' %}
                <span class="status returned">Return Requested</span>
            {% else %}
                <span class="status">Out for Delivery</span>
            {% endif %}
            
            <small style="color:#888;">Order Date: {{ o['date'] }}</small>
            <hr style="border:0; border-top:1px dashed #eee; margin:10px 0;">
            
            {% for item in o['order_items'] %}
                • <b>{{ item['name'] }}</b> (₹{{ item['price'] }})<br>
            {% endfor %}
            
            <br>
            <b>Payment Method:</b> {{ o['payment'] }}<br>
            <b>Delivery Charge:</b> <span style="color:green; font-weight:bold;">FREE</span><br>
            <b>Shipping Address:</b> {{ o['address'] }}<br>
            
            <hr style="border:0; border-top:1px dashed #eee; margin:10px 0;">
            <h3 style="margin:0 0 10px 0; color:#d63031;">Total Paid: ₹{{ o['total'] }}</h3>

            {% if o['status'] == 'Active' %}
                <a href="/cancel_order/{{ loop.index0 }}" class="action-btn btn-cancel">Cancel Order</a>
                <a href="/return_order/{{ loop.index0 }}" class="action-btn btn-return">Return Order</a>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <div class="order"><p>No orders placed yet!</p></div>
    {% endif %}
</body>
</html>
"""

# ==========================================
# ROUTES & LOGIC
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
    
    cart = session.get('cart', [])
    user = session.get('user')
    return render_template_string(HOME_HTML, products=filtered_products, cart_count=len(cart), user=user)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return redirect(url_for('home'))
    return render_template_string(PRODUCT_DETAIL_HTML, product=product)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email in USERS and USERS[email]['password'] == password:
            session['user'] = USERS[email]
            flash("Logged in successfully!")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials!")
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!")
    return redirect(url_for('home'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart
        flash(f"{product['name']} added to cart!")
    return redirect(request.referrer or url_for('home'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(p['price'] for p in cart)
    return render_template_string(CART_HTML, cart=cart, total=total)

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('home'))

    payment_method = request.form.get('payment_method', 'UPI / Online')
    total = sum(p['price'] for p in cart)
    
    user = session.get('user', {"name": "Om Prakash", "phone": "07973813354"})

    new_order = {
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "order_items": list(cart),
        "total": total,
        "customer_name": user['name'],
        "customer_phone": user.get('phone', '07973813354'),
        "payment": payment_method,
        "status": "Active",
        "address": "Haider enclave, house no. 87 Ladian near, livguard battery factory"
    }

    orders = session.get('orders', [])
    orders.append(new_order)
    session['orders'] = orders
    session['cart'] = []

    items_summary = "\n".join([f"- {item['name']} (₹{item['price']})" for item in new_order['order_items']])
    order_details = (
        f"*Customer:* {new_order['customer_name']}\n"
        f"*Phone:* {new_order['customer_phone']}\n"
        f"*Payment Method:* {payment_method}\n"
        f"*Total Paid:* ₹{total}\n"
        f"*Delivery Status:* FREE Express Shipping\n\n"
        f"*Items:*\n{items_summary}\n\n"
        f"*Address:* {new_order['address']}"
    )
    
    send_telegram_notification(order_details)

    return redirect(url_for('orders'))

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    orders = session.get('orders', [])
    if 0 <= order_id < len(orders):
        orders[order_id]['status'] = 'Cancelled'
        session['orders'] = orders
        flash("Order cancelled successfully.")
    return redirect(url_for('orders'))

@app.route('/return_order/<int:order_id>')
def return_order(order_id):
    orders = session.get('orders', [])
    if 0 <= order_id < len(orders):
        orders[order_id]['status'] = 'Return Requested'
        session['orders'] = orders
        flash("Return request submitted.")
    return redirect(url_for('orders'))

@app.route('/orders')
def orders():
    return render_template_string(
        ORDERS_HTML, 
        orders=session.get('orders', []), 
        cart_count=len(session.get('cart', []))
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
