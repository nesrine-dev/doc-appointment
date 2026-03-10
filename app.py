import os
import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)

def get_db_connection():
    # Checks both possible Vercel names
    url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    if not url:
        return None
    # Neon REQUIRES sslmode=require
    return psycopg2.connect(url, sslmode='require')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed. Check Environment Variables."
        
        cur = conn.cursor()
        # Create table if missing
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE,
                password TEXT
            );
        ''')
        
        cur.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                    (name, email, password))
        
        conn.commit()
        cur.close()
        conn.close()
        return f"<h1>Success! Welcome {name}.</h1>"

    return render_template('register.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/appointment')
def appointment():
    return render_template('appointment.html')
