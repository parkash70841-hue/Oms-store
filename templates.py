# templates.py

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Om's Store Plus</title>
    <style>
        :root { --primary: #212121; --secondary: #d32f2f; --green: #388e3c; --bg: #f5f5f5; --text-dark: #1a1a1a; --text-muted: #757575; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, sans-serif; }
        body { background-color: var(--bg); color: var(--text-dark); padding-bottom: 40px; }
        .navbar { background-color: var(--primary); padding: 12px 16px; color: white; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.2); border-bottom: 3px solid var(--secondary); }
        .nav-top { display: flex; justify-content: space-between; align-items: center; max-width: 600px; margin: 0 auto; }
        .brand { font-size: 1.1rem; font-weight: 700; color: #fff; text-decoration: none; display: flex; align-items: center; gap: 4px; }
        .brand span { background: var(--secondary); color: white; font-size: 0.6rem; padding: 2px 5px; border-radius: 4px; font-weight: 800; text-transform: uppercase; }
        .nav-actions { display: flex; align-items: center; gap: 10px; }
        .nav-btn { color: white; text-decoration: none; font-size: 0.8rem; font-weight: 600; background: rgba(255,255,255,0.15); padding: 5px 10px; border-radius: 4px; }
        .cart-icon { position: relative; color: white; text-decoration: none; font-size: 1.2rem; }
        .cart-badge { position: absolute; top: -6px; right: -10px; background: var(--secondary); color: white; font-size: 0.7rem; font-weight: bold; border-radius: 10px; padding: 2px 6px; }
        .categories { display: flex; gap: 8px; overflow-x: auto; max-width: 600px; margin: 10px auto; padding: 0 10px; }
        .cat-chip { background: white; padding: 6px 14px; border-radius: 16px; font-size: 0.8rem; font-weight: 600; white-space: nowrap; color: var(--text-dark); border: 1px solid #ddd; text-decoration: none; }
        .cat-chip.active { background: var(--primary); color: white; border-color: var(--primary); }
        .banner { max-width: 600px; margin: 10px auto; background: #333; color: white; padding: 12px; border-radius: 8px; text-align: center; font-size: 0.85rem; border-left: 4px solid var(--secondary); }
        .banner strong { color: #ff6b6b; }
        .container { max-width: 600px; margin: 0 auto; padding: 0 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .card { background: white; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; padding: 12px; position: relative; border: 1px solid #e0e0e0; text-decoration: none; color: inherit; }
        .tag { position: absolute; top: 8px; left: 8px; background: #ffebee; color: var(--secondary); font-size: 0.65rem; font-weight: 800; padding: 3px 6px; border-radius: 3px; z-index: 2; }
        .img-box { width: 100%; height: 120px; object-fit: contain; margin-bottom: 8px; }
        .title { font-size: 0.85rem; font-weight: 600; line-height: 1.3; color: var(--text-dark); height: 2.6em; overflow: hidden; margin-bottom: 6px; }
        .rating-row { display: flex; align-items: center; gap: 4px; font-size: 0.75rem; margin-bottom: 6px; }
        .rating-badge { background: var(--primary); color: white; padding: 2px 5px; border-radius: 3px; font-weight: bold; font-size: 0.7rem; }
        .price-row { display: flex; align-items: baseline; gap: 4px; margin-bottom: 10px; flex-wrap: wrap; }
        .price { font-size: 1.05rem; font-weight: 800; color: var(--text-dark); }
        .mrp { font-size: 0.75rem; color: var(--text-muted); text-decoration: line-through; }
        .discount { font-size: 0.75rem; color: var(--secondary); font-weight: 700; }
        .add-btn { background-color: var(--secondary); color: white; text-align: center; border: none; padding: 9px 0; border-radius: 4px; font-weight: 700; font-size: 0.8rem; width: 100%; cursor: pointer; text-transform: uppercase; }
        .toast { visibility: hidden; min-width: 250px; background-color: var(--primary); color: #fff; text-align: center; border-radius: 8px; padding: 14px 20px; position: fixed; z-index: 2000; left: 50%; bottom: 30px; transform: translateX(-50%); font-size: 0.85rem; font-weight: 600; border-bottom: 3px solid var(--secondary); display: flex; align-items: center; justify-content: space-between; gap: 10px; }
        .toast.show { visibility: visible; animation: fadein 0.4s, fadeout 0.4s 2.5s; }
        .toast-btn { color: #ff6b6b; text-decoration: none; font-weight: bold; }
        @keyframes fadein { from { bottom: 0; opacity: 0; } to { bottom: 30px; opacity: 1; } }
        @keyframes fadeout { from { bottom: 30px; opacity: 1; } to { bottom: 0; opacity: 0; } }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-top">
            <a href="/" class="brand">Om's Store <span>Plus</span></a>
            <div class="nav-actions">
                <a href="/orders" class="nav-btn">📦 My Orders</a>
                <a href="/cart" class="cart-icon">🛒<span class="cart-badge" id="cartBadge">{{ cart_count }}</span></a>
            </div>
        </div>
    </div>
    <div class="banner">🎉 Use promo code <strong>OM20</strong> for 20% OFF or <strong>SAVE100</strong> for ₹100 OFF!</div>
    <div class="categories">
        <a href="/" class="cat-chip {% if selected_cat == 'All' %}active{% endif %}">All Items</a>
        <a href="/?cat=Audio" class="cat-chip {% if selected_cat == 'Audio' %}active{% endif %}">Audio</a>
        <a href="/?cat=Wearables" class="cat-chip {% if selected_cat == 'Wearables' %}active{% endif %}">Wearables</a>
        <a href="/?cat=Accessories" class="cat-chip {% if selected_cat == 'Accessories' %}active{% endif %}">Accessories</a>
    </div>
    <div class="container">
        <div class="grid">
            {% for product in products %}
            <div class="card">
                <span class="tag">{{ product.tag }}</span>
                <a href="/product/{{ product.id }}" style="text-decoration:none; color:inherit;">
                    <img src="{{ product.image }}" class="img-box" alt="{{ product.name }}">
                    <div class="title">{{ product.name }}</div>
                </a>
                <div class="rating-row">
                    <span class="rating-badge">★ {{ product.rating }}</span>
                    <span style="color:var(--text-muted);">({{ product.reviews }})</span>
                </div>
                <div class="price-row">
                    <span class="price">₹{{ "%.2f"|format(product.price) }}</span>
                    <span class="mrp">₹{{ "%.2f"|format(product.mrp) }}</span>
                    <span class="discount">{{ product.discount }}</span>
                </div>
                <button onclick="addToCart({{ product.id }}, '{{ product.name }}')" class="add-btn">ADD TO CART</button>
            </div>
            {% endfor %}
        </div>
    </div>
    <div id="toast" class="toast">
        <span id="toastMsg">Item added to cart!</span>
        <a href="/cart" class="toast-btn">VIEW CART →</a>
    </div>
    <script>
        function addToCart(productId, productName) {
            fetch('/api/add/' + productId)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cartBadge').innerText = data.cart_count;
                    var toast = document.getElementById("toast");
                    document.getElementById("toastMsg").innerText = "Added: " + productName.substring(0, 18) + "...";
                    toast.className = "toast show";
                    setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);
                });
        }
    </script>
</body>
</html>
"""

PRODUCT_DETAIL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ product.name }} - Om's Store</title>
    <style>
        :root { --primary: #212121; --secondary: #d32f2f; --green: #388e3c; --bg: #f5f5f5; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, sans-serif; }
        body { background-color: var(--bg); padding-bottom: 40px; }
        .navbar { background-color: var(--primary); padding: 12px 16px; color: white; position: sticky; top: 0; z-index: 1000; border-bottom: 3px solid var(--secondary); }
        .nav-top { display: flex; justify-content: space-between; align-items: center; max-width: 600px; margin: 0 auto; }
        .brand { font-size: 1.1rem; font-weight: 700; color: #fff; text-decoration: none; }
        .container { max-width: 600px; margin: 12px auto; padding: 0 10px; }
        .card { background: white; border-radius: 8px; padding: 16px; border: 1px solid #e0e0e0; margin-bottom: 12px; }
        .product-img { width: 100%; height: 220px; object-fit: contain; margin-bottom: 15px; }
        .title { font-size: 1.1rem; font-weight: 700; color: #1a1a1a; margin-bottom: 8px; }
        .price-row { display: flex; align-items: baseline; gap: 8px; margin: 10px 0; }
        .price { font-size: 1.3rem; font-weight: 800; color: #1a1a1a; }
        .mrp { font-size: 0.9rem; color: #757575; text-decoration: line-through; }
        .discount { font-size: 0.9rem; color: var(--secondary); font-weight: bold; }
        .add-btn { background-color: var(--secondary); color: white; border: none; padding: 14px; border-radius: 4px; font-weight: 800; font-size: 1rem; width: 100%; cursor: pointer; text-transform: uppercase; margin-top: 10px; }
        .policy-box { background: #ffebee; border-left: 3px solid var(--secondary); padding: 10px 12px; font-size: 0.8rem; margin-top: 12px; color: #333; }
        .suggestions-title { font-weight: 800; font-size: 0.95rem; text-transform: uppercase; margin: 20px 0 10px; color: #555; }
        .sugg-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .sugg-card { background: white; border-radius: 8px; padding: 10px; border: 1px solid #e0e0e0; text-decoration: none; color: inherit; }
        .sugg-img { width: 100%; height: 80px; object-fit: contain; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-top">
            <a href="/" class="brand">← Back to Store</a>
            <a href="/cart" style="color:white; text-decoration:none;">🛒 Cart</a>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <img src="{{ product.image }}" class="product-img" alt="{{ product.name }}">
            <div class="title">{{ product.name }}</div>
            <div class="price-row">
                <span class="price">₹{{ "%.2f"|format(product.price) }}</span>
                <span class="mrp">₹{{ "%.2f"|format(product.mrp) }}</span>
                <span class="discount">{{ product.discount }}</span>
            </div>
            <p style="font-size:0.85rem; color:#555; line-height:1.5;">{{ product.description }}</p>
            <div class="policy-box">
                🔄 <strong>7-Day Easy Returns & Replacements:</strong> Eligible for free return or exchange within 7 days of delivery.
            </div>
            <button onclick="addToCart({{ product.id }})" class="add-btn">ADD TO CART</button>
        </div>

        <div class="suggestions-title">You Might Also Like</div>
        <div class="sugg-grid">
            {% for item in suggestions %}
            <a href="/product/{{ item.id }}" class="sugg-card">
                <img src="{{ item.image }}" class="sugg-img">
                <div style="font-size:0.8rem; font-weight:600; height:2.4em; overflow:hidden; margin-top:5px;">{{ item.name }}</div>
                <div style="font-size:0.85rem; font-weight:800; color:var(--secondary); margin-top:4px;">₹{{ "%.2f"|format(item.price) }}</div>
            </a>
            {% endfor %}
        </div>
    </div>

    <script>
        function addToCart(productId) {
            fetch('/api/add/' + productId)
                .then(response => response.json())
                .then(data => { alert('Added to Cart!'); });
        }
    </script>
</body>
</html>
"""

CART_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout - Om's Store</title>
    <style>
        :root { --primary: #212121; --secondary: #d32f2f; --green: #388e3c; --bg: #f5f5f5; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, sans-serif; }
        body { background-color: var(--bg); padding-bottom: 30px; }
        .header { background: var(--primary); color: white; padding: 14px 16px; text-align: center; font-weight: 700; font-size: 1.1rem; border-bottom: 3px solid var(--secondary); }
        .container { max-width: 500px; margin: 12px auto; padding: 0 10px; }
        .card { background: white; border-radius: 8px; padding: 16px; border: 1px solid #e0e0e0; margin-bottom: 12px; }
        .summary-title { font-size: 0.85rem; font-weight: 800; color: #555; text-transform: uppercase; margin-bottom: 10px; }
        .coupon-box { display: flex; gap: 8px; margin-bottom: 12px; }
        .coupon-input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; text-transform: uppercase; font-weight: bold; }
        .coupon-btn { background: var(--primary); color: white; border: none; padding: 0 16px; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .price-row { display: flex; justify-content: space-between; margin: 6px 0; font-size: 0.9rem; }
        .discount-text { color: var(--secondary); font-weight: bold; }
        .grand-total { border-top: 2px solid #eee; padding-top: 10px; font-size: 1.1rem; font-weight: 900; color: #1a1a1a; }
        .payment-tabs { display: flex; gap: 8px; margin: 10px 0; }
        .pay-tab { flex: 1; padding: 10px 5px; text-align: center; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; font-size: 0.8rem; font-weight: bold; cursor: pointer; color: #555; }
        .pay-tab.active { background: #ffebee; border-color: var(--secondary); color: var(--secondary); }
        .pay-section { display: none; margin-top: 10px; padding: 12px; background: #fafafa; border-radius: 6px; border: 1px solid #eee; }
        .pay-section.active { display: block; }
        input, textarea { width: 100%; padding: 10px; margin: 6px 0; border: 1px solid #ccc; border-radius: 4px; font-size: 0.9rem; }
        .row-2 { display: flex; gap: 8px; }
        .btn-order { background: var(--secondary); color: white; border: none; width: 100%; padding: 14px; border-radius: 4px; font-weight: 800; font-size: 1rem; cursor: pointer; margin-top: 12px; text-transform: uppercase; }
        .msg { font-size: 0.8rem; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight: bold; }
        .msg-success { background: #e8f5e9; color: var(--green); border-left: 3px solid var(--green); }
        .msg-err { background: #ffebee; color: var(--secondary); border-left: 3px solid var(--secondary); }
    </style>
</head>
<body>
    <div class="header">Order Checkout</div>
    <div class="container">
        {% if items %}
        <div class="card">
            <div class="summary-title">Apply Promo Code</div>
            {% if msg %}
                <div class="msg {% if 'Applied' in msg %}msg-success{% else %}msg-err{% endif %}">{{ msg }}</div>
            {% endif %}
            <form action="/apply_coupon" method="POST" class="coupon-box">
                <input type="text" name="coupon_code" class="coupon-input" placeholder="e.g. OM20" value="{{ applied_coupon }}">
                <button type="submit" class="coupon-btn">APPLY</button>
            </form>
        </div>
        <div class="card">
            <div class="summary-title">Price Details</div>
            <div class="price-row"><span>Subtotal ({{ items|length }} items)</span><span>₹{{ "%.2f"|format(subtotal) }}</span></div>
            {% if discount > 0 %}
            <div class="price-row discount-text"><span>Coupon Discount ({{ applied_coupon }})</span><span>-₹{{ "%.2f"|format(discount) }}</span></div>
            {% endif %}
            <div class="price-row"><span>Delivery Fee</span><span class="discount-text">FREE</span></div>
            <div class="price-row grand-total"><span>Total Payable</span><span>₹{{ "%.2f"|format(total) }}</span></div>
        </div>
        <div class="card">
            <div class="summary-title">Shipping & Payment Options</div>
            <form action="/checkout" method="POST">
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="tel" name="phone" placeholder="10-Digit Mobile Number" required>
                <textarea name="address" rows="2" placeholder="Full Delivery Address" required></textarea>
                <div class="summary-title" style="margin-top:15px;">Select Payment Method</div>
                <div class="payment-tabs">
                    <div class="pay-tab active" onclick="switchPay('card', this)">💳 Card</div>
                    <div class="pay-tab" onclick="switchPay('upi', this)">📱 UPI</div>
                    <div class="pay-tab" onclick="switchPay('cod', this)">💵 COD</div>
                </div>
                <input type="hidden" name="payment_mode" id="pay_mode_input" value="Credit / Debit Card">
                <div id="card_section" class="pay-section active">
                    <input type="text" name="card_number" placeholder="Card Number (16 Digits)" maxlength="16">
                    <div class="row-2">
                        <input type="text" name="card_exp" placeholder="MM/YY" maxlength="5">
                        <input type="password" name="card_cvv" placeholder="CVV" maxlength="3">
                    </div>
                </div>
                <div id="upi_section" class="pay-section">
                    <input type="text" name="upi_id" placeholder="Enter UPI ID (e.g. name@paytm)">
                </div>
                <div id="cod_section" class="pay-section">
                    <p style="font-size:0.85rem; color:#333;">Pay cash when your order is delivered to your doorstep.</p>
                </div>
                <button type="submit" class="btn-order">PAY ₹{{ "%.2f"|format(total) }} & PLACE ORDER</button>
            </form>
        </div>
        {% else %}
        <div class="card" style="text-align: center; padding: 30px;">
            <p style="color: #878787;">Your cart is empty!</p>
        </div>
        {% endif %}
        <a href="/" style="display:block; text-align:center; color:#d32f2f; font-weight:bold; text-decoration:none; margin-top:15px;">← Continue Shopping</a>
    </div>
    <script>
        function switchPay(type, element) {
            document.querySelectorAll('.pay-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.pay-section').forEach(s => s.classList.remove('active'));
            element.classList.add('active');
            if(type === 'card') {
                document.getElementById('card_section').classList.add('active');
                document.getElementById('pay_mode_input').value = "Credit / Debit Card";
            } else if(type === 'upi') {
                document.getElementById('upi_section').classList.add('active');
                document.getElementById('pay_mode_input').value = "UPI / Mobile Wallet";
            } else {
                document.getElementById('cod_section').classList.add('active');
                document.getElementById('pay_mode_input').value = "Cash On Delivery";
            }
        }
    </script>
</body>
</html>
"""

ORDERS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"