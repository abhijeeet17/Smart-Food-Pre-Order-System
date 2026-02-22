#!/bin/bash
echo "============================================================"
echo "  LPU Smart Food System - Setup Script (Mac/Linux)"
echo "============================================================"

echo ""
echo "[1/5] Creating virtual environment..."
python3 -m venv venv

echo ""
echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "*** IMPORTANT: Make sure you have:"
echo "   1. MySQL installed and running"
echo "   2. Created database: CREATE DATABASE lpu_food_db;"
echo "   3. Updated food_system/settings.py with your MySQL credentials"
echo ""
read -p "Press Enter to continue after setting up MySQL..."

echo ""
echo "[4/5] Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "[5/5] Loading sample data..."
python manage.py loaddata orders/fixtures/sample_data.json

echo ""
echo "============================================================"
echo "  Setup Complete!"
echo "============================================================"
echo ""
echo "Now run:"
echo "  python manage.py createsuperuser"
echo "  python manage.py runserver"
echo ""
echo "Then visit: http://127.0.0.1:8000"
