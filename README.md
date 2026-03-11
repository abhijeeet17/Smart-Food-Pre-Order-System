# 🍽️ Smart Food Pre-Ordering System - LPU Campus

![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![AI](https://img.shields.io/badge/AI-Demand%20Prediction-orange.svg)

A comprehensive, AI-powered food pre-ordering system designed for LPU campus to reduce crowd congestion and optimize food ordering experience.

## 🌟 Key Features

### 👨‍🎓 **For Students**
- Browse menu from 4 food stalls (Snack Corner, Beverage Hub, Meal Station, Fast Food Zone)
- Pre-order food with fixed time slot selection
- Real-time order tracking with status updates
- QR code for each order
- View order history and favorites
- Rate and review items
- Get AI-powered recommendations
- Cancel orders before preparation

### 🍳 **For Vendors**
- Dedicated dashboard for each stall
- Manage incoming orders (Accept/Reject/Update status)
- Add/Edit/Delete menu items
- Mark items as "Out of Stock"
- View daily sales summary (₹ earned, items sold)
- 7-day order history
- Peak hours analytics for their stall
- Real-time order notifications

### 👨‍💼 **For Admins**
- View system-wide analytics
- Monitor all stalls and orders
- Peak hours heatmap across campus
- Manage users and stalls

### 🤖 **AI Features**
- **Demand Prediction**: Predict rush hours using historical data
- **Smart Recommendations**: "Trending Now" and "Popular Items"
- **Wait Time Estimation**: Real-time preparation time based on queue
- **Peak Hours Heatmap**: Visual display of busiest times

## 🎨 Design Highlights

### **Orange/Amber Theme** (Completely Different from Attendance System)
- Primary Colors: Vibrant Orange (#FF6B35), Deep Amber (#FF9500)
- Font: Poppins (vs Outfit in attendance)
- Layout: Grid-based with food images (vs Card-based vertical)
- Navigation: Bottom + Top (vs Top only)
- Style: Fun, appetizing, energetic (vs Professional, academic)
- Buttons: Fully rounded pills (vs Rounded rectangles)
- Cards: 30px border radius (vs 20px)

## 📁 Project Structure

```
food_ordering_system/
│
├── food_system/              # Django project
│   ├── settings.py          # Configuration with TIME_SLOTS
│   ├── urls.py              # Main URL routing
│   └── wsgi.py/asgi.py      # Server configs
│
├── core/                    # Main application
│   ├── models.py           # Database models:
│   │                        # - UserProfile (Student/Vendor/Admin)
│   │                        # - FoodStall (4 stalls)
│   │                        # - MenuItem (food items)
│   │                        # - Order (with QR code)
│   │                        # - OrderItem, Favorite, Review
│   │
│   ├── analytics.py        # AI Features:
│   │                        # - Demand prediction
│   │                        # - Peak hours heatmap
│   │                        # - Wait time estimation
│   │                        # - Trending items
│   │
│   ├── views.py            # All view functions
│   ├── forms.py            # Registration & order forms
│   ├── urls.py             # App URL patterns
│   │
│   └── templates/          # HTML templates
│       ├── base.html       # Orange-themed base
│       └── core/           # All pages
│
├── media/                  # Uploaded files
│   ├── menu_items/         # Food images
│   └── qr_codes/          # Order QR codes
│
├── requirements.txt        # Dependencies
├── manage.py              # Django management
└── README.md              # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Step 1: Extract & Navigate
```bash
cd food_ordering_system
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Admin (Optional)
```bash
python manage.py createsuperuser
```

### Step 6: Run Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

## 💡 Usage Guide

### Initial Setup

1. **Create Food Stalls** (Admin Panel)
   - Login to: `http://127.0.0.1:8000/admin/`
   - Create 4 food stalls:
     - Snack Corner (snacks)
     - Beverage Hub (beverages)
     - Meal Station (meals)
     - Fast Food Zone (fastfood)

2. **Register Vendors**
   - Go to: `/register/vendor/`
   - Register one vendor per stall
   - Each vendor gets assigned to their stall

3. **Register Students**
   - Go to: `/register/student/`
   - Register with registration number
   - Students can immediately start ordering

4. **Add Menu Items** (Vendors)
   - Login as vendor
   - Go to "Menu" → "Add Item"
   - Add food items with images, prices

### Student Workflow

1. **Browse Menu**
   - Click "Browse" to see all stalls
   - Filter by stall, category, dietary type
   - View AI recommendations

2. **Add to Cart**
   - Click items to add to cart
   - Adjust quantities
   - See live total

3. **Checkout**
   - Select time slot (Morning/Lunch/Evening)
   - Add special instructions
   - Place order (Mock payment)
   - Get QR code

4. **Track Order**
   - View "My Orders"
   - See real-time status:
     - 🟡 Pending → 🔵 Accepted → 🟠 Preparing → 🟢 Ready
   - Scan QR code at pickup

5. **Review**
   - After pickup, rate items
   - Help others decide

### Vendor Workflow

1. **View Orders**
   - See incoming orders in real-time
   - Accept or reject orders
   - Update status as you prepare

2. **Manage Menu**
   - Add new items
   - Edit prices/availability
   - Mark items "Out of Stock"

3. **View Analytics**
   - Today's sales (₹ earned)
   - Items sold
   - Peak hours for your stall
   - 7-day history

## 🤖 AI Features Explained

### 1. Demand Prediction
- Analyzes last 7 days of orders
- Predicts orders for each time slot
- Shows expected rush hours

### 2. Peak Hours Heatmap
- Visual color intensity shows busy times
- Morning (10:00-11:00)
- Lunch (12:00-13:30) - Usually highest
- Evening (15:00-16:30)

### 3. Wait Time Estimation
- Calculates based on:
  - Current orders in queue
  - Item preparation time
  - Stall workload
- Shows: "Estimated ready in 15 minutes"

### 4. Smart Recommendations
- **Trending Now**: Most ordered this week
- **Popular Items**: Ordered in last 2 hours
- **Personalized**: Based on your order history

## 📊 Database Models

### Key Relationships
- **User** → **UserProfile** (One-to-One)
- **User (Vendor)** → **FoodStall** (One-to-One)
- **FoodStall** → **MenuItem** (One-to-Many)
- **Student** → **Order** (One-to-Many)
- **Order** → **OrderItem** (One-to-Many)
- **Student** → **Favorite** → **MenuItem** (Many-to-Many)
- **Student** → **Review** → **MenuItem** (Many-to-Many)

## 🎯 Key Differences from Attendance System

| Feature | Attendance System | Food Ordering System |
|---------|------------------|---------------------|
| **Colors** | Purple/Indigo (#6366f1) | Orange/Amber (#FF6B35) |
| **Font** | Outfit | Poppins |
| **Layout** | Vertical cards | Grid with images |
| **Icons** | Fingerprint, users | Utensils, food |
| **Navigation** | Top navbar | Top + dynamic |
| **Style** | Professional/Academic | Fun/Appetizing |
| **Buttons** | Rounded rectangles | Full pills (50px radius) |
| **Theme** | Cool/Tech | Warm/Food |

## 📱 Features Implemented

✅ Multi-user system (Student/Vendor/Admin)
✅ 4 food stalls with separate vendors
✅ Fixed time slot pre-ordering
✅ Real-time order tracking
✅ QR code generation for orders
✅ Cart system with live updates
✅ Order history & favorites
✅ Ratings & reviews
✅ Mock payment system
✅ Cancel orders (if not preparing)
✅ Vendor dashboard with sales
✅ Menu management (CRUD)
✅ AI demand prediction
✅ Peak hours heatmap
✅ Wait time estimation
✅ Smart recommendations
✅ Daily specials/offers
✅ Dietary filters (Veg/Non-Veg/Jain)
✅ Search & filter
✅ Responsive design (Mobile & Desktop)

## 🧪 Testing Scenarios

1. **Register 2 vendors**, assign to different stalls
2. **Register 5 students**
3. **Add 10-15 menu items** per stall with images
4. **Students place orders** for different time slots
5. **Vendors accept and update** order status
6. **Check AI predictions** after some orders
7. **View peak hours heatmap**
8. **Test cancel orders** functionality
9. **Add reviews and ratings**
10. **Check vendor analytics**

## 🔒 Security

- Password hashing
- CSRF protection
- User authentication required
- Vendor isolation (see only their stall)
- Student data privacy

## 📈 Future Enhancements

- Real payment gateway integration
- SMS/Email notifications
- Mobile app (React Native)
- Live chat with vendors
- Group ordering
- Loyalty points
- Monthly meal plans



**Made with ❤️ for LPU Project II - Smart Food Pre-Ordering System**

*Reducing Campus Crowd Through Smart Technology*
﻿# Smart-Food-Pre-Order-System


