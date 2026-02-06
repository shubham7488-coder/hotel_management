from flask import Flask, request, jsonify, send_from_directory, render_template_string
import sqlite3
import os
import datetime

app = Flask(__name__, static_url_path='', static_folder='.')

# Database Setup
DB_NAME = "hotel.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, email TEXT, check_in TEXT, check_out TEXT,
                  guests INTEGER, room_type TEXT, status TEXT,
                  room_no TEXT, payment_method TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Migration: Add columns if they don't exist
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN room_no TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN payment_method TEXT")
    except sqlite3.OperationalError:
        pass

    # Orders Table
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  guest_name TEXT, room_no TEXT, item_name TEXT,
                  price TEXT, payment_method TEXT, meal_category TEXT,
                  status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Migration for orders: Add meal_category if it doesn't exist
    try:
        c.execute("ALTER TABLE orders ADD COLUMN meal_category TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

# Initialize API
init_db()

# Routes
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('.', 'admin.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/book', methods=['POST'])
def book_room():
    data = request.json
    name = data.get('name')
def book():
    data = request.json
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    c.execute('''INSERT INTO bookings (name, email, check_in, check_out, guests, room_type, status, room_no, payment_method)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['name'], data['email'], data['check_in'], data['check_out'],
               data['guests'], data['room_type'], 'Pending',
               data.get('room_no', 'N/A'), data.get('payment_method', 'N/A')))
    conn.commit()
    conn.close()
    return jsonify({"message": "Booking successful!"}), 201

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.json
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    c.execute('''INSERT INTO orders (guest_name, room_no, item_name, price, payment_method, meal_category, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data['guest_name'], data.get('room_no', 'N/A'), data['item_name'],
               data['price'], data['payment_method'], data.get('meal_category', 'N/A'), 'Pending'))
    conn.commit()
    conn.close()
    return jsonify({"message": "Order placed successfully!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    password = data.get('password')
    # Simple hardcoded password for demo
    if password == 'admin123':
        return jsonify({'status': 'success', 'token': 'fake-jwt-token'})
    return jsonify({'status': 'error', 'message': 'Invalid password'}), 401

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    # In a real app, verify token here
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bookings ORDER BY created_at DESC')
    bookings = []
    for row in c.fetchall():
        # Handle rows with potentially different column counts if DB was old
        booking = {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "check_in": row[3],
            "check_out": row[4],
            "guests": row[5],
            "room_type": row[6],
            "status": row[7]
        }
        if len(row) > 8: # Check if room_no and payment_method columns exist
            booking["room_no"] = row[8]
            booking["payment_method"] = row[9]
        # created_at is row[10] if all columns exist
        if len(row) > 10:
            booking["created_at"] = row[10]
        bookings.append(booking)
    conn.close()
    return jsonify(bookings)

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Booking deleted'})

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
def update_status(booking_id):
    data = request.json
    status = data.get('status')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': f'Status updated to {status}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
