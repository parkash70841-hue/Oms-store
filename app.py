from flask import Flask, render_template_string, session, redirect, url_for, request
from datetime import datetime
import requests
import razorpay

app = Flask(__name__)
app.secret_key = 'oms_store_master_key_2026'

# ⬇️ CONFIGURATION SETTINGS ⬇️
TELEGRAM_BOT_TOKEN = "8988154095: AAEgrUNdKGA_iuQcav4CMi-HR YeOfqsI4Rg"
TELEGRAM_CHAT_ID = "7867296083"

# Get free test keys from https://dashboard.razorpay.com/
RAZORPAY_KEY_ID = "rzp_test_YOUR_KEY_ID"
RAZORPAY_KEY_SECRET = "YOUR_KEY_SECRET"

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

COUPONS = {"OM20": 20, "SAVE100": 100}
USERS = {}  # Temporary user database {email: {name, phone, password}}

PRODUCTS = [
    {"id": 1, "name": "Sony WH-1000XM5 Wireless Headphones", "category": "Audio", "price": 24999.00, "mrp": 29999.00, "discount": "16% OFF", "rating": 4.8, "reviews": 1240, "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80", "tag": "Bestseller", "description": "Industry-leading noise canceling with two processors and 8 microphones."},
    {"id": 2, "name": "Apple Watch Series 9 GPS 45mm", "category": "Wearables", "price": 32900.00, "mrp": 38900.00, "discount": "15% OFF", "rating": 4.9, "reviews": 850, "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80", "tag": "Trending", "description": "S9 SiP enables a super-bright display and double-tap gesture interaction."},
    {"id": 3, "name": "Logitech MX Master 3S Wireless Mouse", "category": "Accessories", "price": 8499.00, "mrp": 9999.00, "discount": "15% OFF", "rating": 4.7, "reviews": 2100, "image": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&q=80", "tag": "Top Rated", "description": "Ergonomic precision mouse with Quiet Clicks and 8K DPI tracking on glass."},
    {"id": 4, "name": "JBL Flip 6 Portable Bluetooth Speaker", "category": "Audio", "price": 6999.00, "mrp": 9999.00, "discount": "30% OFF", "rating": 4.6, "reviews": 540, "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500&q=80", "tag": "Hot Deal", "description": "Louder, more powerful sound with IP67 waterproof design."}
]

CSS = """<style>
:root{--primary:#212121;--secondary:#d32f2f;--green:#388e3c;--bg:#f5f5f5;}
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif;}
body{background:var(--bg);color:#1a1a1a;padding-bottom:30px;}
.navbar{background:var(--primary);padding:12px 16px;color:#fff;position:sticky;top:0;z-index:1000;border-bottom:3px solid var(--secondary);}
.nav-top{display:flex;justify-content:space-between;align-items:center;max-width:600px;margin:0 auto;}
.brand{font-size:1.1rem;font-weight:700;color:#fff;text-decoration:none;display:flex;align-items:center;gap:4px;}
.brand span{background:var(--secondary);color:#fff;font-size:0.6rem;padding:2px 5px;border-radius:4px;font-weight:800;}
.nav-actions{display:flex;align-items:center;gap:8px;}
.nav-btn{color:#fff;text-decoration:none;font-size:0.75rem;font-weight:600;background:rgba(255,255,255,0.15);padding:5px 8px;border-radius:4px;}
.cart-icon{position:relative;color:#fff;text-decoration:none;font-size:1.2rem;}
.cart-badge{position:absolute;top:-6px;right:-10px;background:var(--secondary);color:#fff;font-size:0.7rem;font-weight:700;border-radius:10px;padding:2px 6px;}
.categories{display:flex;gap:8px;overflow-x:auto;max-width:600px;margin:10px auto;padding:0 10px;}
.cat-chip{background:#fff;padding:6px 14px;border-radius:16px;font-size:0.8rem;font-weight:600;color:#1a1a1a;border:1px solid #ddd;text-decoration:none;white-space:nowrap;}
.cat-chip.active{background:var(--primary);color:#fff;}
.banner{max-width:600px;margin:10px auto;background:#333;color:#fff;padding:12px;border-radius:8px;text-align:center;font-size:0.85rem;border-left:4px solid var(--secondary);}
.container{max-width:600px;margin:0 auto;padding:0 10px;}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.card{background:#fff;border-radius:8px;padding:12px;position:relative;border:1px solid #e0e0e0;display:flex;flex-direction:column;justify-content:space-between;text-decoration:none;color:inherit;}
.tag{position:absolute;top:8px;left:8px;background:#ffebee;color:var(--secondary);font-size:0.65rem;font-weight:800;padding:3px 6px;border-radius:3px;z-index:2;}
.img-box{width:100%;height:120px;object-fit:contain;margin-bottom:8px;}
.title{font-size:0.85rem;font-weight:600;line-height:1.3;height:2.6em;overflow:hidden;margin-bottom:6px;}
.rating-badge{background:var(--primary);color:#fff;padding:2px 5px;border-radius:3px;font-weight:700;font-size:0.7rem;}
.price{font-size:1.05rem;font-weight:800;}
.mrp{font-size:0.75rem;color:#757575;text-decoration:line-through;}
.discount{font-size:0.75rem;color:var(--secondary);font-weight:700;}
.add-btn{background:var(--secondary);color:#fff;border:none;padding:9px 0;border-radius:4px;font-weight:700;font-size:0.8rem;width:100%;cursor:pointer;}
.toast{visibility:hidden;min-width:250px;background:var(--primary);color:#fff;border-radius:8px;padding:14px 20px;position:fixed;z-index:2000;left:50%;bottom:30px;transform:translateX(-50%);font-size:0.85rem;border-bottom:3px solid var(--secondary);display:flex;justify-content:space-between;align-items:center;}
.toast.show{visibility:visible;animation:fadein 0.4s,fadeout 0.4s 2.5s;}
@keyframes fadein{from{bottom:0;opacity:0;}to{bottom:30px;opacity:1;}}
@keyframes fadeout{from{bottom:30px;opacity:1;}to{bottom:0;opacity:0;}}
.pay-tab{flex:1;padding:10px 5px;text-align:center;background:#f8f9fa;border:1px solid #ddd;border-radius:4px;font-size:0.8rem;font-weight:700;cursor:pointer;}
.pay-tab.active{background:#ffebee;border-color:var(--secondary);color:var(--secondary);}
.pay-sec{display:none;margin-top:10px;padding:12px;background:#fafafa;border:1px solid #eee;border-radius:6px;}
.pay-sec.active{display:block;}
input,textarea,select{width:100%;padding:10px;margin:6px 0;border:1px solid #ccc;border-radius:4px;font-size:0.9rem;}
</style>"""

NAVBAR_HTML = """
<div class="navbar"><div class="nav-top">
    <a href="/" class="brand">Om's Store <span>Plus</span></a>
    <div class="nav-actions">
        {% if user %}
            <span style="font-size:0.75rem;font-weight:bold;">👤 {{ user.name.split()[0] }}</span>
            <a href="/logout" class="nav-btn">Logout</a>
        {% else %}
            <a href="/login" class="nav-btn">Login</a>
        {% endif %}
        <a href="/orders" class="nav-btn">📦 Orders</a>
        <a href="/cart" class="cart-icon">🛒<span class="cart-badge" id="cb">{{ cart_count }}</span></a>
    </div>
</div></div>
"""

HOME_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Om's Store Plus</title></head><body>
""" + NAVBAR_HTML + """
<div class="banner">🎉 Code <strong style="color:#ff6b6b">OM20</strong> for 20% OFF or <strong style="color:#ff6b6b">SAVE100</strong> for ₹100 OFF!</div>
<div class="categories">
    <a href="/" class="cat-chip {% if selected_cat == 'All' %}active{% endif %}">All Items</a>
    <a href="/?cat=Audio" class="cat-chip {% if selected_cat == 'Audio' %}active{% endif %}">Audio</a>
    <a href="/?cat=Wearables" class="cat-chip {% if selected_cat == 'Wearables' %}active{% endif %}">Wearables</a>
    <a href="/?cat=Accessories" class="cat-chip {% if selected_cat == 'Accessories' %}active{% endif %}">Accessories</a>
</div>
<div class="container"><div class="grid">
    {% for p in products %}
    <div class="card">
        <span class="tag">{{ p.tag }}</span>
        <a href="/product/{{ p.id }}"><img src="{{ p.image }}" class="img-box"><div class="title">{{ p.name }}</div></a>
        <div style="font-size:0.75rem;margin-bottom:6px;"><span class="rating-badge">★ {{ p.rating }}</span> <span style="color:#757575">({{ p.reviews }})</span></div>
        <div style="margin-bottom:10px;"><span class="price">₹{{ "%.2f"|format(p.price) }}</span> <span class="mrp">₹{{ "%.2f"|format(p.mrp) }}</span> <span class="discount">{{ p.discount }}</span></div>
        <button onclick="addCart({{ p.id }}, '{{ p.name }}')" class="add-btn">ADD TO CART</button>
    </div>
    {% endfor %}
</div></div>
<div id="toast" class="toast"><span id="tmsg">Item added!</span><a href="/cart" style="color:#ff6b6b;font-weight:bold;text-decoration:none;">VIEW CART →</a></div>
<script>
function addCart(id, name){
    fetch('/api/add/'+id).then(r=>r.json()).then(d=>{
        document.getElementById('cb').innerText = d.cart_count;
        var t = document.getElementById("toast");
        document.getElementById("tmsg").innerText = "Added: " + name.substring(0, 16) + "...";
        t.className = "toast show";
        setTimeout(function(){ t.className = t.className.replace("show", ""); }, 3000);
    });
}
</script></body></html>"""

LOGIN_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Login / Sign Up</title></head><body>
""" + NAVBAR_HTML + """
<div class="container" style="margin-top:20px;">
    <div class="card" style="padding:20px;">
        <h3 style="margin-bottom:10px;text-align:center;">{{ mode|upper }} TO YOUR ACCOUNT</h3>
        {% if msg %}<div style="font-size:0.8rem;padding:8px;border-radius:4px;margin-bottom:10px;background:#ffebee;color:var(--secondary);font-weight:bold;">{{ msg }}</div>{% endif %}
        <form action="/auth" method="POST">
            <input type="hidden" name="mode" value="{{ mode }}">
            {% if mode == 'signup' %}
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="tel" name="phone" placeholder="Mobile Number" required>
            {% endif %}
            <input type="email" name="email" placeholder="Email Address" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" class="add-btn" style="margin-top:10px;padding:12px;font-size:0.9rem;">{{ mode|upper }}</button>
        </form>
        <div style="text-align:center;margin-top:15px;font-size:0.85rem;">
            {% if mode == 'login' %}
                Don't have an account? <a href="/signup" style="color:var(--secondary);font-weight:bold;">Sign Up</a>
            {% else %}
                Already registered? <a href="/login" style="color:var(--secondary);font-weight:bold;">Login</a>
            {% endif %}
        </div>
    </div>
</div></body></html>"""

PRODUCT_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>{{ p.name }}</title></head><body>
""" + NAVBAR_HTML + """
<div class="container" style="margin-top:12px;">
    <div class="card">
        <img src="{{ p.image }}" style="width:100%;height:220px;object-fit:contain;margin-bottom:15px;">
        <div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;">{{ p.name }}</div>
        <div style="margin:10px 0;"><span class="price" style="font-size:1.3rem;">₹{{ "%.2f"|format(p.price) }}</span> <span class="mrp">₹{{ "%.2f"|format(p.mrp) }}</span> <span class="discount">{{ p.discount }}</span></div>
        <p style="font-size:0.85rem;color:#555;line-height:1.5;">{{ p.description }}</p>
        <div style="background:#ffebee;border-left:3px solid var(--secondary);padding:10px;font-size:0.8rem;margin-top:12px;">🔄 <strong>7-Day Easy Returns:</strong> Free return or exchange within 7 days.</div>
        <button onclick="addCart({{ p.id }}, '{{ p.name }}')" class="add-btn" style="margin-top:12px;">ADD TO CART</button>
    </div>
</div>
<script>function addCart(id, name){ fetch('/api/add/'+id).then(r=>r.json()).then(d=>{ alert('Added to Cart!'); }); }</script></body></html>"""

CART_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Checkout</title>
<script src="https://checkout.razorpay.com/v1/checkout.js"></script></head><body>
""" + NAVBAR_HTML + """
<div class="container" style="margin-top:12px;">
    {% if items %}
    <div class="card" style="margin-bottom:12px;">
        <div style="font-size:0.85rem;font-weight:800;color:#555;margin-bottom:10px;">PRICE DETAILS</div>
        <div style="display:flex;justify-content:space-between;margin:6px 0;font-size:0.9rem;"><span>Subtotal ({{ items|length }} items)</span><span>₹{{ "%.2f"|format(subtotal) }}</span></div>
        {% if discount > 0 %}<div style="display:flex;justify-content:space-between;margin:6px 0;font-size:0.9rem;color:var(--secondary);font-weight:bold;"><span>Coupon Discount</span><span>-₹{{ "%.2f"|format(discount) }}</span></div>{% endif %}
        <div style="border-top:2px solid #eee;padding-top:10px;font-size:1.1rem;font-weight:900;display:flex;justify-content:space-between;"><span>Total Payable</span><span>₹{{ "%.2f"|format(total) }}</span></div>
    </div>
    <div class="card">
        <div style="font-size:0.85rem;font-weight:800;color:#555;margin-bottom:10px;">SHIPPING & PAYMENT</div>
        <form id="checkoutForm" action="/checkout" method="POST">
            <input type="text" name="name" placeholder="Full Name" value="{{ user.name if user else '' }}" required>
            <input type="tel" name="phone" placeholder="10-Digit Mobile Number" value="{{ user.phone if user else '' }}" required>
            <textarea name="address" rows="2" placeholder="Full Delivery Address" required></textarea>
            
            <div style="font-size:0.85rem;font-weight:800;color:#555;margin:15px 0 10px;">SELECT PAYMENT METHOD</div>
            <select name="payment_mode" id="pmSelect">
                <option value="Online">Online Payment (UPI / Cards / Netbanking)</option>
                <option value="Cash On Delivery">Cash On Delivery (COD)</option>
            </select>
            <button type="submit" class="add-btn" style="margin-top:12px;padding:14px;font-size:1rem;">PROCEED TO PAY ₹{{ "%.2f"|format(total) }}</button>
        </form>
    </div>
    {% else %}<div class="card" style="text-align:center;padding:30px;"><p style="color:#878787;">Your cart is empty!</p></div>{% endif %}
</div></body></html>"""

ORDERS_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>My Orders</title></head><body>
""" + NAVBAR_HTML + """
<div class="container" style="margin-top:12px;">
    {% if orders %}
        {% for o in orders %}
        <div class="card" style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#888;">
                <span>{{ o.date }}</span>
                <span style="background:#ffebee;color:var(--secondary);font-weight:bold;padding:3px 8px;border-radius:4px;">{{ o.status }}</span>
            </div>
            <div style="margin:12px 0;">{% for i in o.order_items %}<div style="font-weight:600;">• {{ i.name }} (₹{{ "%.2f"|format(i.price) }})</div>{% endfor %}</div>
            <div style="font-size:0.8rem;color:#555;line-height:1.5;"><strong>Customer:</strong> {{ o.name }} ({{ o.phone }})<br><strong>Payment:</strong> {{ o.payment_mode }}<br><strong>Address:</strong> {{ o.address }}</div>
            <div style="font-weight:800;border-top:1px dashed #ccc;padding-top:10px;margin-top:10px;display:flex;justify-content:space-between;"><span>Total Paid</span><span style="color:var(--secondary);">₹{{ "%.2f"|format(o.total) }}</span></div>
        </div>
        {% endfor %}
    {% else %}<div class="card" style="text-align:center;"><p style="color:#888;">No orders placed yet!</p></div>{% endif %}
</div></body></html>"""

# TELEGRAM BOT ALERT FUNCTION
def send_telegram_alert(order):
    try:
        items = "\n".join([f"• {i['name']} (₹{i['price']})" for i in order['order_items']])
        msg = (
            f"🚨 *NEW ORDER RECEIVED!*\n\n"
            f"👤 *Customer:* {order['name']}\n"
            f"📞 *Phone:* {order['phone']}\n"
            f"📍 *Address:* {order['address']}\n"
            f"💳 *Payment:* {order['payment_mode']}\n"
            f"💰 *Total Paid:* ₹{order['total']}\n\n"
            f"📦 *Items Ordered:*\n{items}"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print("Telegram Error:", e)

# ROUTES & LOGIC

@app.route('/')
def home():
    cat = request.args.get('cat', 'All')
    cart = session.get('cart', [])
    user = session.get('user')
    filtered = [p for p in PRODUCTS if p['category'] == cat] if cat != 'All' else PRODUCTS
    return render_template_string(HOME_HTML, products=filtered, cart_count=len(cart), selected_cat=cat, user=user)

@app.route('/login')
def login():
    return render_template_string(LOGIN_HTML, mode='login', user=session.get('user'), cart_count=len(session.get('cart', [])))

@app.route('/signup')
def signup():
    return render_template_string(LOGIN_HTML, mode='signup', user=session.get('user'), cart_count=len(session.get('cart', [])))

@app.route('/auth', methods=['POST'])
def auth():
    mode = request.form.get('mode')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if mode == 'signup':
        USERS[email] = {
            "name": request.form.get('name'),
            "phone": request.form.get('phone'),
            "email": email,
            "password": password
        }
        session['user'] = USERS[email]
        return redirect('/')
    else:
        if email in USERS and USERS[email]['password'] == password:
            session['user'] = USERS[email]
            return redirect('/')
        return render_template_string(LOGIN_HTML, mode='login', msg='Invalid Email or Password', user=None, cart_count=len(session.get('cart', [])))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    p = next((x for x in PRODUCTS if x['id'] == product_id), None)
    if not p: return redirect('/')
    return render_template_string(PRODUCT_HTML, p=p, user=session.get('user'), cart_count=len(session.get('cart', [])))

@app.route('/api/add/<int:product_id>')
def api_add_to_cart(product_id):
    if 'cart' not in session: session['cart'] = []
    p = next((x for x in PRODUCTS if x['id'] == product_id), None)
    if p:
        cart = session['cart']
        cart.append(p)
        session['cart'] = cart
    return {"status": "success", "cart_count": len(session['cart'])}

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    sub = sum(x['price'] for x in cart)
    code = session.get('applied_coupon', '')
    disc = round(sub * 0.2, 2) if code == 'OM20' else (min(100, sub) if code == 'SAVE100' else 0)
    tot = round(max(sub - disc, 0), 2)
    return render_template_string(CART_HTML, items=cart, subtotal=sub, discount=disc, total=tot, user=session.get('user'), cart_count=len(cart))

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart: return redirect('/')
    sub = sum(x['price'] for x in cart)
    code = session.get('applied_coupon', '')
    disc = round(sub * 0.2, 2) if code == 'OM20' else (min(100, sub) if code == 'SAVE100' else 0)
    
    order = {
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "name": request.form.get('name'),
        "phone": request.form.get('phone'),
        "address": request.form.get('address'),
        "payment_mode": request.form.get('payment_mode'),
        "total": round(max(sub - disc, 0), 2),
        "status": "Paid & Confirmed" if request.form.get('payment_mode') == 'Online' else "COD Confirmed",
        "order_items": list(cart)
    }
    
    send_telegram_alert(order)
    
    orders = session.get('orders', [])
    orders.insert(0, order)
    session['orders'] = orders
    session.pop('cart', None)
    return redirect(url_for('view_orders'))

@app.route('/orders')
def view_orders():
    return render_template_string(ORDERS_HTML, orders=session.get('orders', []), user=session.get('user'), cart_count=len(session.get('cart', [])))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

