from flask import Flask, render_template_string, session, redirect, url_for, request
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'oms_store_master_key_2026'

COUPONS = {"OM20": 20, "SAVE100": 100}

PRODUCTS = [
    {"id": 1, "name": "Sony WH-1000XM5 Wireless Headphones", "category": "Audio", "price": 24999.00, "mrp": 29999.00, "discount": "16% OFF", "rating": 4.8, "reviews": 1240, "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80", "tag": "Bestseller", "description": "Industry-leading noise canceling with two processors and 8 microphones. Magnificent sound quality."},
    {"id": 2, "name": "Apple Watch Series 9 GPS 45mm", "category": "Wearables", "price": 32900.00, "mrp": 38900.00, "discount": "15% OFF", "rating": 4.9, "reviews": 850, "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80", "tag": "Trending", "description": "S9 SiP enables a super-bright display and a magical new double-tap gesture interaction."},
    {"id": 3, "name": "Logitech MX Master 3S Wireless Mouse", "category": "Accessories", "price": 8499.00, "mrp": 9999.00, "discount": "15% OFF", "rating": 4.7, "reviews": 2100, "image": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&q=80", "tag": "Top Rated", "description": "Ergonomic precision mouse with Quiet Clicks and 8K DPI tracking on glass."},
    {"id": 4, "name": "JBL Flip 6 Portable Bluetooth Speaker", "category": "Audio", "price": 6999.00, "mrp": 9999.00, "discount": "30% OFF", "rating": 4.6, "reviews": 540, "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500&q=80", "tag": "Hot Deal", "description": "Louder, more powerful sound with 2-way speaker system, IP67 waterproof and dustproof design."}
]

CSS = """<style>
:root{--primary:#212121;--secondary:#d32f2f;--green:#388e3c;--bg:#f5f5f5;}
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif;}
body{background:var(--bg);color:#1a1a1a;padding-bottom:30px;}
.navbar{background:var(--primary);padding:12px 16px;color:#fff;position:sticky;top:0;z-index:1000;border-bottom:3px solid var(--secondary);}
.nav-top{display:flex;justify-content:space-between;align-items:center;max-width:600px;margin:0 auto;}
.brand{font-size:1.1rem;font-weight:700;color:#fff;text-decoration:none;display:flex;align-items:center;gap:4px;}
.brand span{background:var(--secondary);color:#fff;font-size:0.6rem;padding:2px 5px;border-radius:4px;font-weight:800;}
.nav-actions{display:flex;align-items:center;gap:10px;}
.nav-btn{color:#fff;text-decoration:none;font-size:0.8rem;font-weight:600;background:rgba(255,255,255,0.15);padding:5px 10px;border-radius:4px;}
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
input,textarea{width:100%;padding:10px;margin:6px 0;border:1px solid #ccc;border-radius:4px;font-size:0.9rem;}
</style>"""

HOME_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Om's Store Plus</title></head><body>
<div class="navbar"><div class="nav-top"><a href="/" class="brand">Om's Store <span>Plus</span></a><div class="nav-actions"><a href="/orders" class="nav-btn">📦 My Orders</a><a href="/cart" class="cart-icon">🛒<span class="cart-badge" id="cb">{{ cart_count }}</span></a></div></div></div>
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

PRODUCT_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>{{ p.name }}</title></head><body>
<div class="navbar"><div class="nav-top"><a href="/" class="brand">← Back to Store</a><a href="/cart" style="color:#fff;text-decoration:none;">🛒 Cart</a></div></div>
<div class="container" style="margin-top:12px;">
    <div class="card">
        <img src="{{ p.image }}" style="width:100%;height:220px;object-fit:contain;margin-bottom:15px;">
        <div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;">{{ p.name }}</div>
        <div style="margin:10px 0;"><span class="price" style="font-size:1.3rem;">₹{{ "%.2f"|format(p.price) }}</span> <span class="mrp">₹{{ "%.2f"|format(p.mrp) }}</span> <span class="discount">{{ p.discount }}</span></div>
        <p style="font-size:0.85rem;color:#555;line-height:1.5;">{{ p.description }}</p>
        <div style="background:#ffebee;border-left:3px solid var(--secondary);padding:10px;font-size:0.8rem;margin-top:12px;">🔄 <strong>7-Day Easy Returns & Replacements:</strong> Eligible for free return or exchange within 7 days.</div>
        <button onclick="addCart({{ p.id }}, '{{ p.name }}')" class="add-btn" style="margin-top:12px;">ADD TO CART</button>
    </div>
    <div style="font-weight:800;font-size:0.95rem;margin:20px 0 10px;color:#555;">YOU MIGHT ALSO LIKE</div>
    <div class="grid">
        {% for s in suggestions %}
        <a href="/product/{{ s.id }}" class="card">
            <img src="{{ s.image }}" style="width:100%;height:80px;object-fit:contain;">
            <div style="font-size:0.8rem;font-weight:600;height:2.4em;overflow:hidden;margin-top:5px;">{{ s.name }}</div>
            <div style="font-size:0.85rem;font-weight:800;color:var(--secondary);margin-top:4px;">₹{{ "%.2f"|format(s.price) }}</div>
        </a>
        {% endfor %}
    </div>
</div>
<script>
function addCart(id, name){ fetch('/api/add/'+id).then(r=>r.json()).then(d=>{ alert('Added to Cart!'); }); }
</script></body></html>"""

CART_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Checkout</title></head><body>
<div class="navbar"><div class="nav-top" style="justify-content:center;font-weight:700;">Order Checkout</div></div>
<div class="container" style="margin-top:12px;">
    {% if items %}
    <div class="card" style="margin-bottom:12px;">
        <div style="font-size:0.85rem;font-weight:800;color:#555;margin-bottom:10px;">APPLY PROMO CODE</div>
        {% if msg %}<div style="font-size:0.8rem;padding:8px;border-radius:4px;margin-bottom:10px;background:#e8f5e9;color:var(--green);font-weight:bold;">{{ msg }}</div>{% endif %}
        <form action="/apply_coupon" method="POST" style="display:flex;gap:8px;">
            <input type="text" name="coupon_code" placeholder="e.g. OM20" value="{{ applied_coupon }}" style="text-transform:uppercase;font-weight:bold;margin:0;">
            <button type="submit" style="background:var(--primary);color:#fff;border:none;padding:0 16px;border-radius:4px;font-weight:bold;">APPLY</button>
        </form>
    </div>
    <div class="card" style="margin-bottom:12px;">
        <div style="font-size:0.85rem;font-weight:800;color:#555;margin-bottom:10px;">PRICE DETAILS</div>
        <div style="display:flex;justify-content:space-between;margin:6px 0;font-size:0.9rem;"><span>Subtotal ({{ items|length }} items)</span><span>₹{{ "%.2f"|format(subtotal) }}</span></div>
        {% if discount > 0 %}<div style="display:flex;justify-content:space-between;margin:6px 0;font-size:0.9rem;color:var(--secondary);font-weight:bold;"><span>Coupon Discount</span><span>-₹{{ "%.2f"|format(discount) }}</span></div>{% endif %}
        <div style="display:flex;justify-content:space-between;margin:6px 0;font-size:0.9rem;"><span style="color:var(--green);font-weight:bold;">Delivery Fee</span><span style="color:var(--green);font-weight:bold;">FREE</span></div>
        <div style="border-top:2px solid #eee;padding-top:10px;font-size:1.1rem;font-weight:900;display:flex;justify-content:space-between;"><span>Total Payable</span><span>₹{{ "%.2f"|format(total) }}</span></div>
    </div>
    <div class="card">
        <div style="font-size:0.85rem;font-weight:800;color:#555;margin-bottom:10px;">SHIPPING & PAYMENT</div>
        <form action="/checkout" method="POST">
            <input type="text" name="name" placeholder="Full Name" required>
            <input type="tel" name="phone" placeholder="10-Digit Mobile Number" required>
            <textarea name="address" rows="2" placeholder="Full Delivery Address" required></textarea>
            <div style="font-size:0.85rem;font-weight:800;color:#555;margin:15px 0 10px;">SELECT PAYMENT METHOD</div>
            <div style="display:flex;gap:8px;margin:10px 0;">
                <div class="pay-tab active" onclick="sw('card',this)">💳 Card</div>
                <div class="pay-tab" onclick="sw('upi',this)">📱 UPI</div>
                <div class="pay-tab" onclick="sw('cod',this)">💵 COD</div>
            </div>
            <input type="hidden" name="payment_mode" id="pm" value="Credit / Debit Card">
            <div id="card_sec" class="pay-sec active"><input type="text" placeholder="Card Number (16 Digits)" maxlength="16"><div style="display:flex;gap:8px;"><input type="text" placeholder="MM/YY" maxlength="5"><input type="password" placeholder="CVV" maxlength="3"></div></div>
            <div id="upi_sec" class="pay-sec"><input type="text" placeholder="Enter UPI ID (e.g. name@paytm)"></div>
            <div id="cod_sec" class="pay-sec"><p style="font-size:0.85rem;">Pay cash when your order is delivered to your doorstep.</p></div>
            <button type="submit" class="add-btn" style="margin-top:12px;padding:14px;font-size:1rem;">PAY ₹{{ "%.2f"|format(total) }} & PLACE ORDER</button>
        </form>
    </div>
    {% else %}<div class="card" style="text-align:center;padding:30px;"><p style="color:#878787;">Your cart is empty!</p></div>{% endif %}
    <a href="/" style="display:block;text-align:center;color:var(--secondary);font-weight:bold;text-decoration:none;margin-top:15px;">← Continue Shopping</a>
</div>
<script>
function sw(t, e) {
    document.querySelectorAll('.pay-tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.pay-sec').forEach(x=>x.classList.remove('active'));
    e.classList.add('active');
    document.getElementById(t+'_sec').classList.add('active');
    document.getElementById('pm').value = t==='card'?'Credit / Debit Card':(t==='upi'?'UPI / Mobile Wallet':'Cash On Delivery');
}
</script></body></html>"""

ORDERS_HTML = CSS + """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>My Orders</title></head><body>
<div class="navbar"><div class="nav-top" style="justify-content:center;font-weight:700;">My Orders</div></div>
<div class="container" style="margin-top:12px;">
    {% if orders %}
        {% for o in orders %}
        <div class="card" style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#888;">
                <span>{{ o.date }}</span>
                {% if o.status == 'Cancelled' %}<span style="background:#eee;color:#666;font-weight:bold;padding:3px 8px;border-radius:4px;">Cancelled</span>
                {% elif o.status == 'Return Requested' %}<span style="background:#eee;color:#666;font-weight:bold;padding:3px 8px;border-radius:4px;">Return Requested</span>
                {% else %}<span style="background:#ffebee;color:var(--secondary);font-weight:bold;padding:3px 8px;border-radius:4px;">✓ Paid & Confirmed</span>{% endif %}
            </div>
            <div style="margin:12px 0;">{% for i in o.order_items %}<div style="font-weight:600;">• {{ i.name }} (₹{{ "%.2f"|format(i.price) }})</div>{% endfor %}</div>
            <div style="font-size:0.8rem;color:#555;line-height:1.5;"><strong>Payment:</strong> {{ o.payment_mode }}<br><strong>Address:</strong> {{ o.address }}</div>
            <div style="font-weight:800;border-top:1px dashed #ccc;padding-top:10px;margin-top:10px;display:flex;justify-content:space-between;"><span>Total Amount</span><span style="color:var(--secondary);">₹{{ "%.2f"|format(o.total) }}</span></div>
            {% if o.status == 'Active' %}
                <div style="margin-top:10px;display:flex;gap:8px;">
                    <a href="/order/action/{{ loop.index0 }}/cancel" style="background:var(--secondary);color:#fff;font-size:0.75rem;font-weight:bold;padding:6px 12px;border-radius:4px;text-decoration:none;">Cancel Order</a>
                    <a href="/order/action/{{ loop.index0 }}/return" style="background:#333;color:#fff;font-size:0.75rem;font-weight:bold;padding:6px 12px;border-radius:4px;text-decoration:none;">Request Return</a>
                </div>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}<div class="card" style="text-align:center;"><p style="color:#888;">No orders placed yet!</p></div>{% endif %}
    <a href="/" style="display:block;text-align:center;color:var(--secondary);font-weight:bold;text-decoration:none;margin-top:20px;">← Back to Store</a>
</div></body></html>"""

# ROUTES & LOGIC

@app.route('/')
def home():
    cat = request.args.get('cat', 'All')
    cart = session.get('cart', [])
    filtered = [p for p in PRODUCTS if p['category'] == cat] if cat != 'All' else PRODUCTS
    return render_template_string(HOME_HTML, products=filtered, cart_count=len(cart), selected_cat=cat)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    p = next((x for x in PRODUCTS if x['id'] == product_id), None)
    if not p: return redirect('/')
    s = [x for x in PRODUCTS if x['id'] != product_id]
    return render_template_string(PRODUCT_HTML, p=p, suggestions=s)

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
    disc = 0
    msg = session.pop('coupon_msg', '')
    if code in COUPONS:
        disc = round(sub * 0.2, 2) if code == 'OM20' else min(100, sub)
    tot = round(max(sub - disc, 0), 2)
    return render_template_string(CART_HTML, items=cart, subtotal=sub, discount=disc, total=tot, applied_coupon=code, msg=msg)

@app.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    code = request.form.get('coupon_code', '').strip().upper()
    if code in COUPONS:
        session['applied_coupon'] = code
        session['coupon_msg'] = f"Coupon '{code}' Applied!"
    else:
        session.pop('applied_coupon', None)
        session['coupon_msg'] = "Invalid Coupon Code!"
    return redirect(url_for('view_cart'))

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
        "status": "Active",
        "order_items": list(cart)
    }
    orders = session.get('orders', [])
    orders.insert(0, order)
    session['orders'] = orders
    session.pop('cart', None)
    session.pop('applied_coupon', None)
    return redirect(url_for('view_orders'))

@app.route('/order/action/<int:order_index>/<string:action>')
def order_action(order_index, action):
    orders = session.get('orders', [])
    if 0 <= order_index < len(orders):
        orders[order_index]['status'] = 'Cancelled' if action == 'cancel' else 'Return Requested'
        session['orders'] = orders
    return redirect(url_for('view_orders'))

@app.route('/orders')
def view_orders():
    return render_template_string(ORDERS_HTML, orders=session.get('orders', []))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
