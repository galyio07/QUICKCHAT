from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import secrets  # For generating a more secure secret key

app = Flask(__name__)

# Generate a secure secret key
app.secret_key = secrets.token_hex(16)

# Path to store user data
USERS_FILE = 'users.json'

def load_users():
    """Load users from JSON file."""
    try:
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except IOError as e:
        print(f"Error saving users: {e}")

@app.route('/')
def index():
    """Redirect to login page."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Enhanced validation
        if not all([username, email, password, confirm_password]):
            return render_template('register.html', error="All fields are required")

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")

        users = load_users()

        if username in users:
            return render_template('register.html', error="Username already exists")

        # Save new user (Note: In production, use password hashing)
        users[username] = {
            'email': email,
            'password': password  # In real app, use secure password hashing
        }

        save_users(users)
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/menu')
def menu():
    """Display menu page."""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', username=session['username'])

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/lawyer/<specialty>')
def lawyer_chat(specialty):
    """Route for lawyer-specific chat."""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('lawyer_chat.html', specialty=specialty)

@app.route('/book_consultation', methods=['POST'])
def book_consultation():
    """Handle consultation booking."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Placeholder for consultation booking logic
    return "Consultation booked successfully"

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)