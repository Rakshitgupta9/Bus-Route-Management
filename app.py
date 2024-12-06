from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection configuration
app.config['MONGO_URI'] = 'mongodb+srv://2021a1r050:gupta%401@bus.dtimg.mongodb.net/bus?retryWrites=true&w=majority&appName=bus'
mongo = PyMongo(app)

# Home route (Login/Register page)
@app.route('/')
def index():
    return render_template('index.html')

# Registration route
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            # Insert user into MongoDB
            mongo.db.users.insert_one({
                'username': username,
                'email': email,
                'phone': phone,
                'password': hashed_password
            })
            flash('Registration successful! Please log in.', 'success')
        except Exception as e:
            flash(f'Error occurred: {str(e)}', 'danger')
            return redirect(url_for('index'))
        return redirect(url_for('index'))

# Login route
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find user by email in MongoDB
        user = mongo.db.users.find_one({'email': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']  # Store username in session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to home page after login
        else:
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('index'))

# Profile route
@app.route('/profile')
def profile():
    if 'username' in session:
        user = mongo.db.users.find_one({'username': session['username']})
        return render_template('profile.html', user=user)
    else:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('index'))

# Home route (Landing page after login)
@app.route('/home')
def home():
    return render_template('home.html')

# Booking route (Book a bus)
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        # Extract form data
        start_location = request.form['start_location']
        end_location = request.form['end_location']
        distance = request.form['distance']
        price = request.form['price']
        date = request.form['date']
        time = request.form['time']

        # Debugging: Print the form data
        print(f"Start Location: {start_location}")
        print(f"End Location: {end_location}")
        print(f"Distance: {distance}")
        print(f"Price: {price}")
        print(f"Date: {date}")
        print(f"Time: {time}")

        # Check if the user is logged in
        if 'username' not in session:
            flash('Please log in to make a booking.', 'danger')
            return redirect(url_for('index'))

        try:
            # Insert booking data into MongoDB
            mongo.db.bookings.insert_one({
                'username': session['username'],  # Fetch username from session
                'start_location': start_location,
                'end_location': end_location,
                'distance': float(distance),  # Convert distance to float
                'price': float(price),  # Convert price to float
                'date': date,
                'time': time,
            })
            flash('Booking successful!', 'success')
        except Exception as e:
            flash(f'Error occurred: {str(e)}', 'danger')

        return redirect(url_for('home'))

    return render_template('booking.html')

# My Bookings route (View all bookings for the user)
@app.route('/my_bookings')
def my_bookings():
    if 'username' not in session:
        flash('Please log in to view your bookings.', 'danger')
        return redirect(url_for('index'))

    # Fetch the user's bookings from MongoDB and convert the cursor to a list
    user_bookings = list(mongo.db.bookings.find({'username': session['username']}))

    return render_template('bookings.html', bookings=user_bookings)

# Cancel Booking route (Cancel a booking)
@app.route('/cancel_booking/<booking_id>')
def cancel_booking(booking_id):
    if 'username' not in session:
        flash('Please log in to cancel a booking.', 'danger')
        return redirect(url_for('index'))

    # Find the booking by its ID
    booking = mongo.db.bookings.find_one({'_id': ObjectId(booking_id)})

    # Check if the booking belongs to the logged-in user
    if booking and booking['username'] == session['username']:
        # Delete the booking
        mongo.db.bookings.delete_one({'_id': ObjectId(booking_id)})
        flash('Booking canceled successfully.', 'success')
    else:
        flash('Booking not found or you do not have permission to cancel this booking.', 'danger')

    return redirect(url_for('my_bookings'))

# About route (Information about the bus management system)
@app.route('/about')
def about():
    return render_template('about.html')

# Contact route (Contact page)
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
