import os
import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)

# This connects to the Neon Database using the secret URL Vercel just created
def get_db_connection():
    # Vercel/Neon use 'DATABASE_URL' or 'POSTGRES_URL'
    # We will try DATABASE_URL first as it's the standard for Neon
    url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(url)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create the table if it's not there yet
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                dob TEXT,
                gender TEXT,
                password TEXT
            );
        ''')
        
        # Insert the data
        cur.execute('INSERT INTO users (name, email, phone, dob, gender, password) VALUES (%s, %s, %s, %s, %s, %s)',
                    (name, email, phone, dob, gender, password))
        
        conn.commit()
        cur.close()
        conn.close()
        return f"<h1>Account created for {name}! Your data is now in the database.</h1>"

    return render_template('register.html')

# Add other routes for doctors and appointments here later!
