from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
import json

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'apple'

# Configuration for MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_management_system'

# Create a MySQL instance to connect to the database
mysql = MySQL(app)

# Route to the home page
@app.route('/')
def index():
    return render_template('frontpage.html')

# Route to handle user registration
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Insert user into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        
        # Redirect to the home page after registration
        return redirect(url_for('index'))

# Route to retrieve user information by username
@app.route('/user/<username>')
def get_user(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_info = cur.fetchone()
    cur.close()
    if user_info:
        return jsonify(user_info), 200  
    else:
        return jsonify({"error": "User not found"}), 404  

# Route to render the registration page
@app.route('/registration')
def registration_page():
    return render_template('registration.html')

# Route to update user password
@app.route('/update_password/<username>', methods=['POST'])
def update_password(username):
    if request.method == 'POST':
        new_password = request.form['new_password']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('welcome'))

# Route to update username
@app.route('/update_username/<username>', methods=['POST'])
def update_username(username):
    if request.method == 'POST':
        new_username = request.form['new_username']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET username = %s WHERE username = %s", (new_username, username))
        mysql.connection.commit()
        cur.close()
        session['username'] = new_username  
        return redirect(url_for('welcome'))

# Route to render the welcome page
@app.route('/welcome')
def welcome():
    if 'username' in session:
        username = session['username'] 
        return redirect(url_for('pacman', username=username)) 
    else:
        return redirect(url_for('login')) 

# Route to handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database to authenticate user
        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = user[0] 
            return redirect(url_for('welcome', username=user[0]))  
        else:
            return "Invalid username or password"  
    else:
        return render_template('login.html')

# Route to handle user logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)  
    return redirect(url_for('index'))  

# Route to handle user deletion
@app.route('/delete_account/<username>', methods=['POST'])
def delete_account(username):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE username = %s", (username,))
        mysql.connection.commit()
        cur.close()
        session.pop('username', None)  # Logout the user after deleting the account
        return redirect(url_for('index'))

@app.route('/pacman/<username>')
def pacman(username):
    return render_template('pacman.html', username=username)

@app.route('/welcomepage/<username>')
def welcomepage(username):
    return render_template('welcomepage.html', username=username)

@app.route('/products/<username>')
def products(username):
    return render_template('products.html', username=username)

@app.route('/account')
def account():
    if 'username' in session:
        username = session['username']
        # Redirect to the welcome page while passing the username
        return redirect(url_for('welcomepage', username=username))
        
@app.route('/product')
def product():
    if 'username' in session:
        username = session['username']
        # Load products data from JSON file
        with open('statics/product.json', 'r') as json_file:
            products_data = json.load(json_file)
        # Render the products template and pass the products data
        return render_template('products.html', username=username, products=products_data)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)


