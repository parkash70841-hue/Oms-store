import os
import random
import requests
import razorpay
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'oms_store_master_key_2026'

# ==========================================
# CONFIGURATION & API KEYS
# ==========================================
TELEGRAM_BOT_TOKEN = "8988154095:AAHIoRgwHA08Mfw1viZFUPdeUpJyjF3dRTI"
TELEGRAM_CHAT_ID = "7867296083"

# Admin Password
ADMIN_PASSWORD = "admin_password_2026"

# Live Razorpay Credentials
RAZORPAY_KEY_ID = "rzp_live_TJitd3iSUTjRvj"
RAZORPAY_KEY_SECRET = "cy9j7FsRBGeneGYybhPP28as"

# Store Settings
STORE_LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3081/3081559.png"
CUSTOMER_CARE_EMAIL = "opr70841@gmail.com"

razor_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def send_telegram_notification(title, details):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{title}\n\n{details}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram Error:", e)

@app.before_request
def make_session_permanent():
    session.permanent = True
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}
    if 'orders' not in session or not isinstance(session['orders'], list):
        session['orders'] = []

# ==========================================
# PRODUCTS DATA
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
# COMMON CSS & ANIMATIONS
# ==========================================
COMMON_STYLE = """
<style>
    * { box-sizing: border-box; }
    html { height: 100%; }
    body { 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
        margin: 0; 
        padding: 0;
        padding-bottom: 70px !important; 
        min-height: 100vh;
        background: #f1f2f6; 
        color: #333; 
        animation: fadeIn 0.3s cubic-bezier(0.39, 0.575, 0.565, 1) both;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Fixed Bottom Nav Bar */
    .bottom-nav { 
        position: fixed !important; 
        bottom: 0 !important; 
        left: 0 !important; 
        right: 0 !important; 
        width: 100% !important; 
        height: 60px !important;
        background: #ffffff !important; 
        border-top: 1px solid #e2e8f0 !important; 
        display: flex !important; 
        justify-content: space-around !important; 
        align-items: center !important; 
        box-shadow: 0 -4px 15px rgba(0,0,0,0.08) !important; 
        z-index: 99999 !important; 
    }
    .nav-item { 
        flex: 1; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center;
        text-decoration: none; 
        color: #718096; 
        font-size: 11px; 
        font-weight: 600; 
        height: 100%;
        transition: color 0.2s ease;
    }
    .nav-item.active { color: #ff4757; }
    .nav-item span { 
        font-size: 20px; 
        height: 22px;
        line-height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2px;
    }

    /* Animated Add to Cart Popup */
    .toast-container { position: fixed; top: 15px; left: 50%; transform: translateX(-50%); z-index: 999999; width: 90%; max-width: 380px; }
    
    @keyframes slidePop {
        0% { transform: scale(0.7) translateY(-50px); opacity: 0; }
        60% { transform: scale(1.05) translateY(5px); opacity: 1; }
        100% { transform: scale(1) translateY(0); opacity: 1; }
    }

    @keyframes cartBounce {
        0%, 100% { transform: scale(1) rotate(0deg); }
        30% { transform: scale(1.3) rotate(-12deg); }
        60% { transform: scale(1.2) rotate(12deg); }
    }

    .toast { 
        background: #111111;
        color: #ffffff; 
        padding: 12px 18px; 
        border-radius: 50px; 
        font-size: 13px; 
        font-weight: 700; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35); 
        animation: slidePop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        display: flex;
        align-items: center;
        gap: 12px;
        border: 2px solid #ff4757;
    }

    .toast-icon {
        background: #ff4757;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        animation: cartBounce 0.6s ease 0.2s;
    }
</style>
"""

# ==========================================
# HTML TEMPLATES
# ==========================================
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Om's Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    """ + COMMON_STYLE + """
    <style>
        body { background: #ffffff; padding-bottom: 80px !important; }

        /* Top Header & Search */
        .home-header { 
            background: #ffffff; 
            position: sticky; 
            top: 0; 
            z-index: 100;
            border-bottom: 1px solid #f0f0f0;
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .header-top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header-brand { display: flex; align-items: center; gap: 10px; }
        .logo-img { width: 32px; height: 32px; object-fit: contain; }
        .brand-title { font-size: 18px; font-weight: 800; color: #111; display: flex; align-items: center; gap: 6px; }
        .brand-title span { background: #ff4757; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 900; }
        
        .header-email-btn { 
            display: flex; 
            align-items: center; 
            gap: 5px; 
            font-size: 11px; 
            font-weight: 700; 
            color: #ff4757; 
            background: #fff0f2; 
            padding: 6px 12px; 
            border-radius: 20px; 
            text-decoration: none; 
        }

        .search-box { display: flex; width: 100%; }
        .search-box input { width: 100%; padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 8px 0 0 8px; font-size: 13px; outline: none; background: #f8f9fa; }
        .search-box button { background: #ff4757; color: white; border: none; padding: 10px 14px; border-radius: 0 8px 8px 0; cursor: pointer; font-weight: bold; }

        
        .header-email-btn { 
            display: flex; 
            align-items: center; 
            gap: 5px; 
            font-size: 11px; 
            font-weight: 700; 
            color: #ff4757; 
            background: #fff0f2; 
            padding: 6px 12px; 
            border-radius: 20px; 
            text-decoration: none; 
        }

        .main-container { padding: 16px; max-width: 600px; margin: auto; }

        /* Hero Banner */
        .hero-banner { 
            position: relative; 
            border-radius: 20px; 
            overflow: hidden; 
            background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.65)), url('https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&q=80'); 
            background-size: cover; 
            background-position: center; 
            padding: 24px 20px; 
            color: white; 
            margin-bottom: 16px; 
        }
        .hero-badge { 
            display: inline-block; 
            background: #ff4757; 
            color: #ffffff; 
            font-size: 11px; 
            font-weight: 700; 
            padding: 5px 12px; 
            border-radius: 20px; 
            margin-bottom: 12px; 
        }
        .hero-title { font-size: 24px; font-weight: 800; line-height: 1.2; margin-bottom: 6px; }
        .hero-sub { font-size: 12px; opacity: 0.9; margin-bottom: 16px; line-height: 1.4; }
        .hero-btn { 
            display: inline-flex; 
            align-items: center; 
            gap: 6px; 
            background: #ffffff; 
            color: #111; 
            font-size: 13px; 
            font-weight: 700; 
            padding: 10px 18px; 
            border-radius: 25px; 
            text-decoration: none; 
        }

        /* Value Badges Row */
        .value-grid { display: flex; gap: 8px; overflow-x: auto; margin-bottom: 24px; padding-bottom: 4px; }
        .value-pill { 
            display: flex; 
            align-items: center; 
            gap: 6px; 
            border: 1px solid #e2e8f0; 
            border-radius: 25px; 
            padding: 8px 14px; 
            font-size: 11px; 
            font-weight: 600; 
            color: #333; 
            white-space: nowrap; 
            background: #ffffff;
        }

        /* Section Headings */
        .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
        .section-title { font-size: 16px; font-weight: 700; color: #111; }
        .see-all { font-size: 12px; font-weight: 600; color: #ff4757; text-decoration: none; }

        /* Categories Circles */
        .cat-scroll { display: flex; gap: 16px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 24px; }
        .cat-item { display: flex; flex-direction: column; align-items: center; text-decoration: none; min-width: 65px; }
        .cat-circle { 
            width: 58px; 
            height: 58px; 
            border-radius: 50%; 
            background: #f8f9fa; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 22px; 
            margin-bottom: 6px; 
            border: 1px solid #f0f0f0;
            transition: transform 0.2s;
        }
        .cat-item:active .cat-circle { transform: scale(0.92); }
        .cat-label { font-size: 11px; font-weight: 600; color: #444; }

        /* Product Grid */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .card { 
            background: #ffffff; 
            border: 1px solid #e2e8f0; 
            border-radius: 14px; 
            overflow: hidden; 
            display: flex; 
            flex-direction: column; 
            position: relative; 
        }
        .card-badges { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; justify-content: space-between; z-index: 2; pointer-events: none; }
        .badge-disc { background: #ff4757; color: white; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 12px; }
        .badge-new { background: #111; color: white; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 12px; }

        .img-box { background: #f9f9fb; height: 140px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .img-box img { width: 100%; height: 100%; object-fit: cover; }

        .card-details { padding: 12px; display: flex; flex-direction: column; flex: 1; }
        .card-brand { font-size: 10px; font-weight: 700; color: #888; text-transform: uppercase; margin-bottom: 2px; }
        .card-title { font-size: 13px; font-weight: 700; color: #111; text-decoration: none; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 32px; }
        .card-rating { font-size: 11px; font-weight: 600; color: #333; margin-bottom: 6px; }
        .card-price-row { font-size: 14px; font-weight: 800; color: #d63031; margin-top: auto; }
        .card-mrp { font-size: 11px; color: #888; text-decoration: line-through; font-weight: normal; margin-left: 4px; }
    </style>
</head>
<body>
    <div class="toast-container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">
            <div class="toast-icon">🛒</div>
            <div>{{ message }}</div>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    </div>

       <!-- Top Header with Search Bar -->
    <div class="home-header">
        <div class="header-top-row">
            <div class="header-brand">
                <img src="{{ logo_url }}" class="logo-img" alt="Logo">
                <div class="brand-title">Om's Store <span>Plus</span></div>
            </div>
            <a href="mailto:{{ email }}" class="header-email-btn">
                ✉️ Customer Care
            </a>
        </div>
        <!-- SEARCH BAR RESTORED -->
        <form action="/" method="GET" class="search-box">
            <input type="text" name="q" placeholder="Search products, brands & categories..." value="{{ request.args.get('q', '') }}">
            <button type="submit">🔍</button>
        </form>
    </div>


    <div class="main-container">
        <!-- Hero Banner -->
        <div class="hero-banner">
            <span class="hero-badge">⚡ Mega Sale · Up to 70% off</span>
            <div class="hero-title">Everything You Need,<br>One Cart.</div>
            <div class="hero-sub">Fashion, Electronics, Home & more — delivered fast.</div>
            <a href="#featured" class="hero-btn">Shop now →</a>
        </div>

        <!-- Trust Badges -->
        <div class="value-grid">
            <div class="value-pill">🚚 Free Shipping</div>
            <div class="value-pill">🛡️ Secure Pay</div>
            <div class="value-pill">🏷️ Best Prices</div>
        </div>

        <!-- Categories -->
        <div class="section-header">
            <div class="section-title">Shop by Category</div>
            <a href="/" class="see-all">See all →</a>
        </div>

        <div class="cat-scroll">
            <a href="/?cat=Audio" class="cat-item">
                <div class="cat-circle">🎧</div>
                <span class="cat-label">Audio</span>
            </a>
            <a href="/?cat=Wearables" class="cat-item">
                <div class="cat-circle">⌚</div>
                <span class="cat-label">Wearables</span>
            </a>
            <a href="/?cat=Accessories" class="cat-item">
                <div class="cat-circle">🖱️</div>
                <span class="cat-label">Accessories</span>
            </a>
            <a href="/" class="cat-item">
                <div class="cat-circle">📱</div>
                <span class="cat-label">Mobiles</span>
            </a>
            <a href="/" class="cat-item">
                <div class="cat-circle">💻</div>
                <span class="cat-label">Laptops</span>
            </a>
        </div>

        <!-- Featured Products Grid -->
        <div class="section-header" id="featured">
            <div class="section-title">Featured</div>
            <a href="/" class="see-all">See all →</a>
        </div>

        <div class="grid">
            {% for p in products %}
            <div class="card">
                <div class="card-badges">
                    <span class="badge-disc">{{ p.discount }}</span>
                    <span class="badge-new">NEW</span>
                </div>
                <a href="/product/{{ p.id }}" class="img-box">
                    <img src="{{ p.image }}">
                </a>
                <div class="card-details">
                    <div class="card-brand">OM'S STORE</div>
                    <a href="/product/{{ p.id }}" class="card-title">{{ p.name }}</a>
                    <div class="card-rating">★ {{ p.rating }} <span style="color:#888;">({{ p.reviews }})</span></div>
                    <div class="card-price-row">
                        ₹{{ p.price }} <span class="card-mrp">₹{{ p.mrp }}</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Bottom Nav Bar -->
    <nav class="bottom-nav">
        <a href="/" class="nav-item active"><span>🏠</span>Home</a>
        <a href="/cart" class="nav-item"><span>🛒</span>Cart</a>
        <a href="/orders" class="nav-item"><span>📦</span>Orders</a>
        {% if user %}
            <a href="/logout" class="nav-item"><span>👤</span>Logout</a>
        {% else %}
            <a href="/login" class="nav-item"><span>👤</span>Account</a>
        {% endif %}
    </nav>

    <script>
        setTimeout(() => {
            const toast = document.querySelector('.toast-container');
            if (toast) {
                toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                toast.style.opacity = '0';
                toast.style.transform = 'translate(-50%, -20px)';
                setTimeout(() => toast.remove(), 500);
            }
        }, 2500);
    </script>
</body>
</html>
"""

PRODUCT_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ product.name }} - Om's Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    """ + COMMON_STYLE + """
    <style>
        body { background: #ffffff; padding-bottom: 140px !important; }
        
        /* Top Navigation Bar */
        .p-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: #fff; border-bottom: 1px solid #eee; position: sticky; top: 0; z-index: 100; }
        .p-header-title { font-size: 16px; font-weight: 600; color: #222; }
        .p-header-icons { display: flex; align-items: center; gap: 12px; }
        .email-icon-btn { color: #ff4757; font-size: 12px; font-weight: bold; text-decoration: none; background: #fff0f2; padding: 4px 10px; border-radius: 15px; }

        /* Image Box & Badge */
        .img-container { position: relative; background: #f9f9fb; width: 100%; text-align: center; }
        .img-container img { width: 100%; max-height: 320px; object-fit: contain; padding: 20px 0; }
        .discount-badge { position: absolute; top: 15px; left: 15px; background: #ff4757; color: white; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }

        /* Product Details Content */
        .p-content { padding: 16px; max-width: 600px; margin: auto; }
        .brand-name { font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
        .p-title { font-size: 20px; font-weight: 700; color: #111; margin: 4px 0 8px; }
        
        .rating-sku { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .rate-box { background: #f5f5f7; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }
        .sku-text { font-size: 11px; color: #888; }

        .price-row { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; }
        .main-price { font-size: 24px; font-weight: 800; color: #d63031; }
        .mrp-price { font-size: 14px; color: #888; text-decoration: line-through; }
        .save-tag { font-size: 13px; color: #27ae60; font-weight: 700; }
        .tax-subtext { font-size: 11px; color: #777; margin-bottom: 16px; }

        /* Stock & Quantity Control */
        .stock-qty-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .stock-pill { background: #e6f4ea; color: #137333; font-size: 12px; font-weight: 700; padding: 6px 12px; border-radius: 20px; }
        .qty-picker { display: flex; align-items: center; border: 1px solid #e2e8f0; border-radius: 20px; padding: 4px 12px; gap: 16px; }
        .qty-picker button { border: none; background: none; font-size: 16px; font-weight: bold; cursor: pointer; color: #333; }

        /* Sections */
        .sec-title { font-size: 14px; font-weight: 700; margin: 20px 0 8px; color: #222; }
        .sec-text { font-size: 13px; color: #555; line-height: 1.5; }

        /* Specs Table */
        .specs-card { border: 1px solid #eee; border-radius: 10px; overflow: hidden; margin-bottom: 20px; }
        .spec-row { display: flex; justify-content: space-between; padding: 10px 14px; font-size: 12px; border-bottom: 1px solid #eee; }
        .spec-row:last-child { border-bottom: none; }
        .spec-key { color: #666; }
        .spec-val { font-weight: 600; color: #111; }

        /* Trust Badges */
        .trust-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin: 20px 0; }
        .trust-card { border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 6px; text-align: center; font-size: 11px; font-weight: 600; color: #333; }
        .trust-card span { display: block; font-size: 16px; margin-bottom: 4px; }

        /* Sticky Bottom Action Bar */
        .p-action-bar { position: fixed; bottom: 60px; left: 0; right: 0; background: white; border-top: 1px solid #eee; padding: 10px 16px; display: flex; align-items: center; gap: 10px; z-index: 999; }
        .wishlist-btn { border: 1px solid #ccc; background: white; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 18px; cursor: pointer; }
        .btn-outline-cart { flex: 1; border: 1px solid #111; background: white; color: #111; font-weight: 700; padding: 12px; border-radius: 25px; text-align: center; text-decoration: none; font-size: 13px; }
        .btn-solid-buy { flex: 1; background: #111111; color: white; font-weight: 700; padding: 12px; border-radius: 25px; text-align: center; text-decoration: none; font-size: 13px; }

        /* Similar Products Carousel */
        .sugg-grid { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 10px; }
        .sugg-card { border: 1px solid #eee; border-radius: 10px; padding: 8px; min-width: 140px; flex-shrink: 0; position: relative; }
        .sugg-card img { width: 100%; height: 100px; object-fit: contain; }
        .sugg-title-text { font-size: 11px; font-weight: 600; margin: 6px 0; color: #222; text-decoration: none; display: block; height: 28px; overflow: hidden; }
        .sugg-price-text { font-size: 12px; font-weight: 700; color: #d63031; }
    </style>
</head>
<body>
    <div class="toast-container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">
            <div class="toast-icon">🛒</div>
            <div>{{ message }}</div>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    </div>

    <!-- Header -->
    <div class="p-header">
        <a href="/" style="text-decoration:none; color:#111; font-weight:bold;">←</a>
        <div class="p-header-title">Product</div>
        <div class="p-header-icons">
            <a href="mailto:{{ email }}" class="email-icon-btn">✉️ Help</a>
        </div>
    </div>

    <!-- Image Container -->
    <div class="img-container">
        <span class="discount-badge">{{ product.discount }}</span>
        <img src="{{ product.image }}">
    </div>

    <!-- Content -->
    <div class="p-content">
        <div class="brand-name">OM'S STORE EXCLUSIVE</div>
        <div class="p-title">{{ product.name }}</div>

        <div class="rating-sku">
            <div class="rate-box">★ {{ product.rating }} <span style="color:#777; font-weight:normal;">({{ product.reviews }} reviews)</span></div>
            <div class="sku-text">SKU: OM-{{ product.id }}026</div>
        </div>

        <div class="price-row">
            <span class="main-price">₹{{ product.price }}</span>
            <span class="mrp-price">₹{{ product.mrp }}</span>
            <span class="save-tag">Save {{ product.discount }}</span>
        </div>
        <div class="tax-subtext">Inclusive of all taxes • Free shipping on orders</div>

        <div class="stock-qty-row">
            <span class="stock-pill">In stock</span>
            <div class="qty-picker">
                <button onclick="decrementQty()">-</button>
                <span id="qty-val" style="font-weight:bold; font-size:13px;">1</span>
                <button onclick="incrementQty()">+</button>
            </div>
        </div>

        <div class="sec-title">Description</div>
        <div class="sec-text">{{ product.description }}</div>

        <div class="sec-title">Specifications</div>
        <div class="specs-card">
            <div class="spec-row">
                <span class="spec-key">Category</span>
                <span class="spec-val">{{ product.category }}</span>
            </div>
            <div class="spec-row">
                <span class="spec-key">Delivery</span>
                <span class="spec-val">{{ product.delivery }}</span>
            </div>
            <div class="spec-row">
                <span class="spec-key">Support</span>
                <span class="spec-val">{{ email }}</span>
            </div>
        </div>

        <div class="trust-grid">
            <div class="trust-card"><span>🚚</span>Fast Ship</div>
            <div class="trust-card"><span>🛡️</span>Authentic</div>
            <div class="trust-card"><span>🔄</span>7-day Return</div>
        </div>

        <div class="sec-title">Similar products</div>
        <div class="sugg-grid">
            {% for p in products %}
            {% if p.id != product.id %}
            <div class="sugg-card">
                <a href="/product/{{ p.id }}"><img src="{{ p.image }}"></a>
                <a href="/product/{{ p.id }}" class="sugg-title-text">{{ p.name }}</a>
                <div class="sugg-price-text">₹{{ p.price }}</div>
            </div>
            {% endif %}
            {% endfor %}
        </div>
    </div>

    <!-- Sticky Bottom Action Bar -->
    <div class="p-action-bar">
        <button class="wishlist-btn">♡</button>
        <a href="/add_to_cart/{{ product.id }}" class="btn-outline-cart">Add to Cart</a>
        <!-- DIRECT BUY NOW ACTION ROUTE -->
        <a href="/buy_now/{{ product.id }}" class="btn-solid-buy">Buy Now</a>
    </div>

    <nav class="bottom-nav">
        <a href="/" class="nav-item"><span>🏠</span>Home</a>
        <a href="/cart" class="nav-item"><span>🛒</span>Cart</a>
        <a href="/orders" class="nav-item"><span>📦</span>Orders</a>
        <a href="/login" class="nav-item"><span>👤</span>Account</a>
    </nav>

    <script>
        let currentQty = 1;
        function incrementQty() {
            currentQty++;
            document.getElementById('qty-val').innerText = currentQty;
        }
        function decrementQty() {
            if (currentQty > 1) {
                currentQty--;
                document.getElementById('qty-val').innerText = currentQty;
            }
        }
        
        setTimeout(() => {
            const toast = document.querySelector('.toast-container');
            if (toast) {
                toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                toast.style.opacity = '0';
                toast.style.transform = 'translate(-50%, -20px)';
                setTimeout(() => toast.remove(), 500);
            }
        }, 2500);
    </script>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>OTP Verification - Om's Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    """ + COMMON_STYLE + """
    <style>
        body { display:flex; justify-content:center; align-items:center; min-height:100vh; padding: 0; }
        .card { background:white; padding:25px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.08); width:300px; text-align:center; }
        input { width:100%; padding:12px; margin:10px 0; border:1px solid #ccc; border-radius:8px; box-sizing:border-box; font-size:14px; }
        .btn { width:100%; background:#111; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:10px; font-size:14px; }
        .back { text-decoration:none; color:#555; font-size:12px; display:block; margin-bottom:15px; text-align:left; }
    </style>
</head>
<body>
    <div class="toast-container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">
            <div class="toast-icon">🔔</div>
            <div>{{ message }}</div>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    </div>

    <div class="card">
        <a href="/" class="back">← Back to Store</a>
        <h2 style="margin-bottom:5px;">OTP Login</h2>
        <p style="font-size:12px; color:#666; margin-bottom:20px;">Enter Mobile No. or Email to get OTP</p>

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

    <nav class="bottom-nav">
        <a href="/" class="nav-item"><span>🏠</span>Home</a>
        <a href="/cart" class="nav-item"><span>🛒</span>Cart</a>
        <a href="/orders" class="nav-item"><span>📦</span>Orders</a>
        <a href="/login" class="nav-item active"><span>👤</span>Account</a>
    </nav>
</body>
</html>
"""

CART_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Your Cart & Checkout</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    """ + COMMON_STYLE + """
    <style>
        body { padding:15px; max-width:600px; margin:auto; }
        .box { background:white; padding:18px; border-radius:12px; margin-bottom:15px; box-shadow:0 2px 8px rgba(0,0,0,0.05); }
        .cart-item { display:flex; align-items:center; gap:12px; padding:12px 0; border-bottom:1px solid #eee; }
        .cart-item img { width:60px; height:60px; object-fit:cover; border-radius:8px; }
        .item-info { flex:1; }
        .item-title { font-size:13px; font-weight:bold; color:#222; margin-bottom:4px; }
        .item-price { font-size:14px; font-weight:bold; color:#d63031; }
        
        .qty-controls { display:flex; align-items:center; gap:8px; margin-top:6px; }
        .qty-btn { background:#f1f2f6; border:1px solid #ccc; width:26px; height:26px; border-radius:5px; display:flex; justify-content:center; align-items:center; font-weight:bold; text-decoration:none; color:#333; font-size:14px; }
        .qty-val { font-size:13px; font-weight:bold; min-width:18px; text-align:center; }
        .delete-btn { color:#e74c3c; text-decoration:none; font-size:16px; margin-left:auto; padding:4px; }

        .form-input { width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:6px; font-size:13px; }
        .pay-option { background:#f8f9fa; border:1px solid #e2e8f0; padding:12px; border-radius:8px; margin:8px 0; font-size:14px; cursor:pointer; }
        .btn { background:#27ae60; color:white; padding:14px; text-align:center; display:block; border-radius:8px; border:none; width:100%; font-size:16px; font-weight:bold; cursor:pointer; margin-top:15px; }
        .back { color:#333; text-decoration:none; display:inline-block; margin-bottom:12px; font-weight:bold; }

        .sugg-title { font-size:15px; font-weight:bold; margin:20px 0 10px 0; color:#222; }
        .sugg-grid { display:flex; gap:10px; overflow-x:auto; padding-bottom:10px; }
        .sugg-card { background:white; border-radius:8px; padding:10px; min-width:140px; box-shadow:0 2px 5px rgba(0,0,0,0.05); text-align:center; flex-shrink:0; }
        .sugg-card img { width:100%; height:80px; object-fit:cover; border-radius:6px; }
        .sugg-name { font-size:11px; font-weight:bold; height:28px; overflow:hidden; margin:5px 0; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; color:#222; text-decoration:none; }
        .sugg-price { color:#d63031; font-weight:bold; font-size:12px; }
        .sugg-btn { background:#111111; color:white; border:none; padding:6px 10px; border-radius:4px; font-size:10px; font-weight:bold; text-decoration:none; display:inline-block; margin-top:5px; transition: background 0.2s; }
        .sugg-btn:hover { background:#333333; }
    </style>
</head>
<body>
    <div class="toast-container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">
            <div class="toast-icon">📦</div>
            <div>{{ message }}</div>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    </div>

    <a href="/" class="back">← Back to Shop</a>
    <h2>Shopping Cart & Checkout</h2>
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

        <form id="checkout-form" onsubmit="handleCheckout(event)">
            <div class="box">
                <h3 style="margin-top:0;">📍 Delivery Address</h3>
                <input type="text" id="delivery_name" name="delivery_name" class="form-input" placeholder="Full Name" required>
                <input type="text" id="delivery_phone" name="delivery_phone" class="form-input" placeholder="10-digit Mobile Number" required>
                <textarea id="delivery_address" name="delivery_address" class="form-input" placeholder="Flat / House No., Street, Landmark, City, Pincode" required style="height:60px; font-family:inherit;"></textarea>
            </div>

            <div class="box">
                <h3 style="margin-top:0;">💳 Payment Method</h3>
                
                <div class="pay-option">
                    <input type="radio" id="radio_online" name="payment_method" value="Online Payment" checked> 💳 <b>Online Payment (Razorpay: UPI / Cards / Netbanking)</b>
                </div>

                <div class="pay-option" style="opacity: 0.6; cursor: not-allowed; background: #f1f2f6;">
                    <input type="radio" id="radio_cod" name="payment_method" value="Cash on Delivery" disabled> 💵 <b style="color:#777;">Cash on Delivery (COD)</b>
                    <div style="color: #e74c3c; font-size: 11px; font-weight: bold; margin-top: 4px; margin-left: 22px;">❌ Not available in your area</div>
                </div>

                <button type="submit" class="btn" id="pay-btn">PAY & PLACE ORDER (₹{{ total }})</button>
            </div>
        </form>
    {% else %}
        <div class="box" style="text-align:center; padding:30px;">
            <p style="font-size:16px; color:#666;">Your cart is empty!</p>
            <a href="/" style="background:#111; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; display:inline-block; font-weight:bold;">Start Shopping</a>
        </div>
    {% endif %}

    <div class="sugg-title">🔥 You Might Also Like</div>
    <div class="sugg-grid">
        {% for p in products %}
        <div class="sugg-card">
            <a href="/product/{{ p.id }}"><img src="{{ p.image }}"></a>
            <a href="/product/{{ p.id }}" class="sugg-name">{{ p.name }}</a>
            <div class="sugg-price">₹{{ p.price }}</div>
            <a href="/add_to_cart/{{ p.id }}" class="sugg-btn">+ ADD</a>
        </div>
        {% endfor %}
    </div>

    <nav class="bottom-nav">
        <a href="/" class="nav-item"><span>🏠</span>Home</a>
        <a href="/cart" class="nav-item active"><span>🛒</span>Cart</a>
        <a href="/orders" class="nav-item"><span>📦</span>Orders</a>
        <a href="/login" class="nav-item"><span>👤</span>Account</a>
    </nav>

    <script>
        async function handleCheckout(event) {
            event.preventDefault();
            const payBtn = document.getElementById('pay-btn');

            const delName = document.getElementById('delivery_name').value;
            const delPhone = document.getElementById('delivery_phone').value;
            const delAddress = document.getElementById('delivery_address').value;

            payBtn.innerText = "Opening Payment Gateway...";
            payBtn.disabled = true;

            const res = await fetch('/create_razorpay_order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: delName, phone: delPhone, address: delAddress })
            });
            const data = await res.json();

            if (data.error) {
                alert("Razorpay Error: " + data.error);
                payBtn.innerText = "PAY & PLACE ORDER (₹{{ total }})";
                payBtn.disabled = false;
                return;
            }

            var options = {
                "key": data.key,
                "amount": data.amount,
                "currency": "INR",
                "name": "Om's Store",
                "description": "Order Payment",
                "order_id": data.id,
                "handler": async function (response) {
                    const verifyRes = await fetch('/verify_payment', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature,
                            delivery_name: delName,
                            delivery_phone: delPhone,
                            delivery_address: delAddress,
                            payment_method: "Online (Razorpay)"
                        })
                    });
                    const verifyData = await verifyRes.json();
                    if (verifyData.status === 'success') {
                        window.location.href = "/orders";
                    } else {
                        alert("Payment Verification Failed!");
                    }
                },
                "prefill": {
                    "name": delName,
                    "contact": delPhone
                },
                "theme": {
                    "color": "#ff4757"
                }
            };
            var rzp1 = new Razorpay(options);
            rzp1.open();
            payBtn.innerText = "PAY & PLACE ORDER (₹{{ total }})";
            payBtn.disabled = false;
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
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    """ + COMMON_STYLE + """
    <style>
        body { padding:15px; max-width:600px; margin:auto; }
        .order-card { background:white; border-radius:12px; padding:18px; margin-bottom:15px; box-shadow:0 3px 10px rgba(0,0,0,0.05); cursor:pointer; position:relative; transition: transform 0.2s; }
        .order-card:hover { transform: translateY(-2px); }
        .order-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
        .badge { padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold; }
        .badge-active { background:#e8f8f0; color:#27ae60; }
        .badge-cancelled { background:#ffe0e0; color:#e74c3c; }
        .item-row { display:flex; justify-content:space-between; font-size:13px; margin:6px 0; color:#485460; }
        .total-row { display:flex; justify-content:space-between; font-weight:bold; font-size:15px; margin-top:12px; padding-top:10px; border-top:1px dashed #ddd; color:#d63031; }
        .click-hint { font-size:11px; color:#ff4757; text-align:right; font-weight:bold; margin-top:8px; }

        .modal { display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.6); z-index:2000; justify-content:center; align-items:center; padding:15px; }
        .modal-content { background:white; border-radius:12px; padding:20px; width:100%; max-width:480px; max-height:85vh; overflow-y:auto; position:relative; animation: fadeIn 0.3s ease; }
        .close-btn { position:absolute; top:12px; right:15px; font-size:22px; cursor:pointer; color:#888; font-weight:bold; }

        .sugg-title { font-size:15px; font-weight:bold; margin:20px 0 10px 0; color:#222; }
        .sugg-grid { display:flex; gap:10px; overflow-x:auto; padding-bottom:10px; }
        .sugg-card { background:white; border-radius:8px; padding:10px; min-width:140px; box-shadow:0 2px 5px rgba(0,0,0,0.05); text-align:center; flex-shrink:0; }
        .sugg-card img { width:100%; height:80px; object-fit:cover; border-radius:6px; }
        .sugg-name { font-size:11px; font-weight:bold; height:28px; overflow:hidden; margin:5px 0; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; color:#222; text-decoration:none; }
        .sugg-price { color:#d63031; font-weight:bold; font-size:12px; }
        .sugg-btn { background:#111111; color:white; border:none; padding:6px 10px; border-radius:4px; font-size:10px; font-weight:bold; text-decoration:none; display:inline-block; margin-top:5px; transition: background 0.2s; }
        .sugg-btn:hover { background:#333333; }
    </style>
</head>
<body>
    <div class="toast-container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">
            <div class="toast-icon">📦</div>
            <div>{{ message }}</div>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    </div>

    <a href="/" style="color:#333; text-decoration:none; display:inline-block; margin-bottom:12px; font-weight:bold;">← Back to Shop</a>
    <h2>My Orders Dashboard</h2>
    
    {% if orders %}
        {% for o in orders %}
        <div class="order-card" onclick="openOrderModal({{ loop.index0 }})">
            <div class="order-header">
                <div>
                    <b>Order #{{ loop.index }}</b><br>
                    <small style="color:#888;">{{ o['date'] }}</small>
                </div>
                
                {% if o['status'] == 'Cancelled' %}
                    <span class="badge badge-cancelled">Cancelled</span>
                {% elif o['status'] == 'Delivered' %}
                    <span class="badge" style="background:#d4edda; color:#155724;">✅ Delivered</span>
                {% elif o['status'] == 'Out for Delivery' %}
                    <span class="badge" style="background:#fff3cd; color:#856404;">🛵 Out for Delivery</span>
                {% elif o['status'] == 'Shipped' %}
                    <span class="badge" style="background:#cce5ff; color:#004085;">🚚 Shipped</span>
                {% else %}
                    <span class="badge badge-active">📦 {{ o['status'] }}</span>
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
            <div class="click-hint">🔍 Tap to view details / cancel →</div>
        </div>

        <div id="modal-{{ loop.index0 }}" class="modal">
            <div class="modal-content">
                <span class="close-btn" onclick="closeOrderModal({{ loop.index0 }})">&times;</span>
                <h3>Order Details #{{ loop.index }}</h3>
                <p style="font-size:12px; color:#666;">Placed on {{ o['date'] }}</p>
                <hr style="border:0; border-top:1px solid #eee;">
                
                <h4>Items Ordered</h4>
                {% for item in o['order_items'] %}
                <div class="item-row">
                    <span><b>{{ item['name'] }}</b> x{{ item['qty'] }}</span>
                    <span>₹{{ item['price'] * item['qty'] }}</span>
                </div>
                {% endfor %}

                <hr style="border:0; border-top:1px solid #eee;">
                <p style="font-size:13px; line-height:1.5;">
                    <b>Customer Name:</b> {{ o['customer_name'] }}<br>
                    <b>Phone:</b> {{ o['customer_phone'] }}<br>
                    <b>Payment Method:</b> {{ o['payment'] }}<br>
                    <b>Delivery Address:</b> {{ o['address'] }}
                </p>

                {% if o['status'] != 'Cancelled' and o['status'] != 'Delivered' %}
                <div style="display:flex; gap:10px; margin-top:20px;">
                    <a href="/cancel_order/{{ loop.index0 }}" style="flex:1; background:#ff4757; color:white; text-align:center; padding:10px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:12px;">Cancel Order</a>
                    <a href="/return_order/{{ loop.index0 }}" style="flex:1; background:#ffa502; color:white; text-align:center; padding:10px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:12px;">Request Return</a>
                </div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="order-card" style="text-align:center; padding:30px;">
            <p style="color:#666;">No orders placed yet!</p>
        </div>
    {% endif %}

    <div class="sugg-title">🔥 Trending Products</div>
    <div class="sugg-grid">
        {% for p in products %}
        <div class="sugg-card">
            <a href="/product/{{ p.id }}"><img src="{{ p.image }}"></a>
            <a href="/product/{{ p.id }}" class="sugg-name">{{ p.name }}</a>
            <div class="sugg-price">₹{{ p.price }}</div>
            <a href="/add_to_cart/{{ p.id }}" class="sugg-btn">+ ADD</a>
        </div>
        {% endfor %}
    </div>

    <nav class="bottom-nav">
        <a href="/" class="nav-item"><span>🏠</span>Home</a>
        <a href="/cart" class="nav-item"><span>🛒</span>Cart</a>
        <a href="/orders" class="nav-item active"><span>📦</span>Orders</a>
        <a href="/login" class="nav-item"><span>👤</span>Account</a>
    </nav>

    <script>
        function openOrderModal(id) {
            document.getElementById('modal-' + id).style.display = 'flex';
        }
        function closeOrderModal(id) {
            document.getElementById('modal-' + id).style.display = 'none';
        }
    </script>
</body>
</html>
"""

# ==========================================
# ROUTES & LOGIC
# ==========================================
@app.route('/', strict_slashes=False)
def home():
    cat = request.args.get('cat')
    search_query = request.args.get('q', '').strip().lower()
    
    filtered_products = PRODUCTS
    if cat:
        filtered_products = [p for p in filtered_products if p['category'] == cat]
    if search_query:
        filtered_products = [p for p in filtered_products if search_query in p['name'].lower() or search_query in p['category'].lower()]
    
    cart = session.get('cart', {})
    cart_count = sum(item['qty'] for item in cart.values())
    user = session.get('user')
    return render_template_string(HOME_HTML, products=filtered_products, cart_count=cart_count, user=user, logo_url=STORE_LOGO_URL, email=CUSTOMER_CARE_EMAIL)

@app.route('/product/<int:product_id>', strict_slashes=False)
def product_detail(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return redirect(url_for('home'))
    return render_template_string(PRODUCT_DETAIL_HTML, product=product, products=PRODUCTS, email=CUSTOMER_CARE_EMAIL)

@app.route('/add_to_cart/<int:product_id>', strict_slashes=False)
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
        flash(f"Added '{product['name']}' to your cart!")
    return redirect(request.referrer or url_for('home'))

@app.route('/buy_now/<int:product_id>', strict_slashes=False)
def buy_now(product_id):
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
    return redirect(url_for('cart'))

@app.route('/login', strict_slashes=False)
def login():
    return render_template_string(LOGIN_HTML, otp_sent=False)

@app.route('/send_otp', methods=['POST'], strict_slashes=False)
def send_otp():
    identifier = request.form.get('identifier', '').strip()
    if not identifier:
        flash("Please enter a valid Mobile Number or Email!")
        return render_template_string(LOGIN_HTML, otp_sent=False)

    otp = str(random.randint(1000, 9999))
    session['generated_otp'] = otp
    session['user_identifier'] = identifier
    flash(f"Your OTP is: {otp}")
    return render_template_string(LOGIN_HTML, otp_sent=True)

@app.route('/verify_otp', methods=['POST'], strict_slashes=False)
def verify_otp():
    user_otp = request.form.get('otp_input')
    if user_otp == session.get('generated_otp'):
        session['user'] = {"name": session.get('user_identifier'), "phone": session.get('user_identifier')}
        flash("Logged in successfully!")
        return redirect(url_for('home'))
    else:
        flash("Invalid OTP! Try again.")
        return render_template_string(LOGIN_HTML, otp_sent=True)

@app.route('/logout', strict_slashes=False)
def logout():
    session.pop('user', None)
    flash("Logged out successfully!")
    return redirect(url_for('home'))

@app.route('/update_qty/<string:product_id>/<string:action>', strict_slashes=False)
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

@app.route('/remove_item/<string:product_id>', strict_slashes=False)
def remove_item(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        flash("Item removed from cart.")
    return redirect(url_for('cart'))

@app.route('/cart', strict_slashes=False)
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['qty'] for item in cart.values())
    return render_template_string(CART_HTML, cart=cart, total=total, products=PRODUCTS)

# ==========================================
# RAZORPAY PAYMENT ENDPOINTS
# ==========================================
@app.route('/create_razorpay_order', methods=['POST'], strict_slashes=False)
def create_razorpay_order():
    cart = session.get('cart', {})
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400

    total = sum(item['price'] * item['qty'] for item in cart.values())
    amount_in_paise = int(total * 100)

    try:
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': 1
        }
        razorpay_order = razor_client.order.create(data=order_data)
        return jsonify({
            'id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'key': RAZORPAY_KEY_ID
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify_payment', methods=['POST'], strict_slashes=False)
def verify_payment():
    data = request.get_json()
    params_dict = {
        'razorpay_order_id': data['razorpay_order_id'],
        'razorpay_payment_id': data['razorpay_payment_id'],
        'razorpay_signature': data['razorpay_signature']
    }

    try:
        razor_client.utility.verify_payment_signature(params_dict)
        
        cart = session.get('cart', {})
        total = sum(item['price'] * item['qty'] for item in cart.values())
        order_items_list = list(cart.values())

        del_name = data.get('delivery_name')
        del_phone = data.get('delivery_phone')
        full_shipping_info = f"{del_name} ({del_phone}), {data.get('delivery_address')}"

        new_order = {
            "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "order_items": order_items_list,
            "total": total,
            "customer_name": del_name,
            "customer_phone": del_phone,
            "payment": f"Online (Razorpay ID: {data['razorpay_payment_id']})",
            "status": "Order Placed",
            "address": full_shipping_info
        }

        orders = session.get('orders', [])
        if not isinstance(orders, list):
            orders = []
        orders.append(new_order)
        
        session['orders'] = orders
        session['cart'] = {}

        items_summary = "\n".join([f"- {item['name']} x{item['qty']} (₹{item['price'] * item['qty']})" for item in order_items_list])
        details = (
            f"*Customer:* {del_name}\n"
            f"*Phone:* {del_phone}\n"
            f"*Payment Method:* Online (Razorpay Paid ✅)\n"
            f"*Razorpay Payment ID:* `{data['razorpay_payment_id']}`\n"
            f"*Total Paid:* ₹{total}\n\n"
            f"*Items:*\n{items_summary}\n\n"
            f"*Address:* {full_shipping_info}"
        )
        send_telegram_notification("💳 *New Online Paid Order Received!*", details)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'failure', 'error': str(e)}), 400

@app.route('/cancel_order/<int:order_id>', strict_slashes=False)
def cancel_order(order_id):
    orders = session.get('orders', [])
    if 0 <= order_id < len(orders):
        orders[order_id]['status'] = 'Cancelled'
        session['orders'] = orders
        o = orders[order_id]
        details = f"⚠️ *Order Cancelled by Customer*\n\n*Customer:* {o['customer_name']}\n*Amount:* ₹{o['total']}"
        send_telegram_notification("❌ *Order Cancellation Alert*", details)
        flash("Order cancelled successfully.")
    return redirect(url_for('orders'))

@app.route('/return_order/<int:order_id>', strict_slashes=False)
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

@app.route('/orders', strict_slashes=False)
def orders():
    return render_template_string(ORDERS_HTML, orders=session.get('orders', []), products=PRODUCTS)

# ==========================================
# ADMIN PORTAL
# ==========================================
@app.route('/admin', strict_slashes=False)
def admin_dashboard():
    if not session.get('is_admin'):
        return render_template_string("""
            <div style="font-family:sans-serif; text-align:center; padding:50px 15px;">
                <h2>🔐 Admin Login</h2>
                <form action="/admin_login" method="POST">
                    <input type="password" name="password" placeholder="Enter Admin Password" style="padding:10px; border:1px solid #ccc; border-radius:6px; font-size:14px;"><br><br>
                    <button type="submit" style="background:#ff4757; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; cursor:pointer;">LOGIN</button>
                </form>
            </div>
        """)
    
    orders = session.get('orders', [])
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Panel - Om's Store</title>
            <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding:15px; background:#f4f4f4; max-width:700px; margin:auto; }
                .box { background:white; border-radius:10px; padding:18px; margin-bottom:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
                .form-input { width:100%; padding:10px; margin:6px 0; border:1px solid #ccc; border-radius:6px; font-size:13px; box-sizing:border-box; }
                .btn-add { background:#27ae60; color:white; border:none; padding:12px; border-radius:6px; font-weight:bold; width:100%; cursor:pointer; font-size:14px; margin-top:8px; }
                .status-badge { padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold; background:#e8f8f0; color:#27ae60; }
                .btn-status { background:#3498db; color:white; padding:6px 10px; border-radius:6px; text-decoration:none; font-size:11px; font-weight:bold; display:inline-block; margin-bottom:4px; }
                .btn-cancel { background:#e74c3c; color:white; padding:6px 10px; border-radius:6px; text-decoration:none; font-size:11px; font-weight:bold; display:inline-block; }
                .p-item { display:flex; align-items:center; justify-content:space-between; padding:10px 0; border-bottom:1px solid #eee; }
                .p-item img { width:45px; height:45px; object-fit:cover; border-radius:6px; }
            </style>
        </head>
        <body>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <h2>👑 Admin Control Panel</h2>
                <a href="/admin_logout" style="color:#777; text-decoration:none; font-size:13px; font-weight:bold;">Logout</a>
            </div>

            <!-- ADD PRODUCT FORM -->
            <div class="box">
                <h3 style="margin-top:0;">➕ Add New Product to Store</h3>
                <form action="/admin/add_product" method="POST">
                    <input type="text" name="name" class="form-input" placeholder="Product Title" required>
                    <div style="display:flex; gap:8px;">
                        <input type="number" step="0.01" name="price" class="form-input" placeholder="Selling Price (₹)" required>
                        <input type="number" step="0.01" name="mrp" class="form-input" placeholder="MRP Price (₹)">
                    </div>
                    <div style="display:flex; gap:8px;">
                        <select name="category" class="form-input">
                            <option value="Audio">Audio</option>
                            <option value="Wearables">Wearables</option>
                            <option value="Accessories">Accessories</option>
                        </select>
                        <input type="text" name="tag" class="form-input" placeholder="Badge Tag (e.g. Bestseller)">
                    </div>
                    <input type="url" name="image" class="form-input" placeholder="Image URL" required>
                    <input type="text" name="delivery" class="form-input" placeholder="Delivery Info">
                    <textarea name="description" class="form-input" placeholder="Product Description..." style="height:60px; font-family:inherit;"></textarea>
                    <button type="submit" class="btn-add">PUBLISH PRODUCT TO STORE</button>
                </form>
            </div>

            <!-- MANAGE PRODUCTS -->
            <div class="box">
                <h3 style="margin-top:0;">📦 Existing Products</h3>
                {% for p in products %}
                <div class="p-item">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="{{ p.image }}">
                        <div>
                            <b>{{ p.name }}</b><br>
                            <small style="color:#d63031; font-weight:bold;">₹{{ p.price }}</small>
                        </div>
                    </div>
                    <a href="/admin/delete_product/{{ p.id }}" style="color:#e74c3c; text-decoration:none; font-weight:bold; font-size:13px;" onclick="return confirm('Remove product?')">🗑️ Delete</a>
                </div>
                {% endfor %}
            </div>

            <!-- ORDERS MANAGEMENT -->
            <div class="box">
                <h3 style="margin-top:0;">📋 Customer Orders</h3>
                {% if orders %}
                    {% for o in orders %}
                    <div style="border-bottom:1px solid #eee; padding-bottom:12px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b>Order #{{ loop.index }}</b>
                            <span class="status-badge">{{ o['status'] }}</span>
                        </div>
                        <p style="font-size:13px; margin:6px 0; color:#555;">
                            <b>Customer:</b> {{ o['customer_name'] }} ({{ o['customer_phone'] }})<br>
                            <b>Total:</b> ₹{{ o['total'] }} | <b>Payment:</b> {{ o['payment'] }}<br>
                            <b>Address:</b> {{ o['address'] }}
                        </p>

                        {% if o['status'] != 'Cancelled' %}
                        <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:8px;">
                            <a href="/admin/update_status/{{ loop.index0 }}/Packed" class="btn-status">📦 Packed</a>
                            <a href="/admin/update_status/{{ loop.index0 }}/Shipped" class="btn-status">🚚 Shipped</a>
                            <a href="/admin/update_status/{{ loop.index0 }}/Out for Delivery" class="btn-status" style="background:#e67e22;">🛵 Out for Delivery</a>
                            <a href="/admin/update_status/{{ loop.index0 }}/Delivered" class="btn-status" style="background:#27ae60;">✅ Delivered</a>
                            <a href="/admin/cancel_order/{{ loop.index0 }}" class="btn-cancel" onclick="return confirm('Cancel order?')">❌ Cancel</a>
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="font-size:13px; color:#777;">No orders placed yet.</p>
                {% endif %}
            </div>

            <a href="/" style="color:#333; font-weight:bold; text-decoration:none;">← Back to Public Store</a>
        </body>
        </html>
    """, products=PRODUCTS)

@app.route('/admin/add_product', methods=['POST'], strict_slashes=False)
def admin_add_product():
    if not session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))

    name = request.form.get('name', '').strip()
    category = request.form.get('category', 'Audio')
    price = float(request.form.get('price', 0))
    mrp = float(request.form.get('mrp', price * 1.2))
    discount = request.form.get('discount', '10% OFF')
    tag = request.form.get('tag', 'New Arrival')
    image = request.form.get('image', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80')
    delivery = request.form.get('delivery', 'FREE Delivery within 2 Days')
    description = request.form.get('description', 'High-quality product from Om\'s Store.')

    new_id = max([p['id'] for p in PRODUCTS], default=0) + 1

    new_product = {
        "id": new_id,
        "name": name,
        "category": category,
        "price": price,
        "mrp": mrp,
        "discount": discount,
        "rating": 5.0,
        "reviews": 1,
        "image": image,
        "tag": tag,
        "delivery": delivery,
        "description": description
    }

    PRODUCTS.append(new_product)
    flash(f"🎉 Product '{name}' added successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_product/<int:product_id>', strict_slashes=False)
def admin_delete_product(product_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))

    global PRODUCTS
    PRODUCTS = [p for p in PRODUCTS if p['id'] != product_id]
    flash("🗑️ Product removed from store.")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_login', methods=['POST'], strict_slashes=False)
def admin_login():
    if request.form.get('password') == ADMIN_PASSWORD:
        session['is_admin'] = True
        flash("Logged into Admin Portal!")
    else:
        flash("Invalid Admin Password!")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_logout', strict_slashes=False)
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

@app.route('/admin/update_status/<int:order_id>/<string:new_status>', strict_slashes=False)
def admin_update_status(order_id, new_status):
    if not session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
        
    orders = session.get('orders', [])
    if 0 <= order_id < len(orders):
        orders[order_id]['status'] = new_status
        session['orders'] = orders
        
        o = orders[order_id]
        details = (
            f"🚚 *Delivery Status Updated*\n\n"
            f"*Order #:* {order_id + 1}\n"
            f"*Customer:* {o['customer_name']}\n"
            f"*New Status:* `{new_status}`\n"
            f"*Phone:* {o['customer_phone']}"
        )
        send_telegram_notification("📦 *Order Tracking Update*", details)
        flash(f"Order #{order_id + 1} marked as {new_status}!")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/cancel_order/<int:order_id>', strict_slashes=False)
def admin_cancel_order(order_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
        
    orders = session.get('orders', [])
    if 0 <= order_id < len(orders):
        orders[order_id]['status'] = 'Cancelled'
        session['orders'] = orders
        
        o = orders[order_id]
        details = (
            f"❌ *Order # {order_id + 1} Cancelled by Admin*\n\n"
            f"*Customer:* {o['customer_name']}\n"
            f"*Phone:* {o['customer_phone']}\n"
            f"*Amount:* ₹{o['total']}"
        )
        send_telegram_notification("⚠️ *Admin Order Cancellation*", details)
        flash("Order cancelled by Admin.")
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
