from flask import Flask, render_template, request, redirect
from twilio.rest import Client
import random

app = Flask(__name__)

# --- TWILIO SETUP ---
# Replace these strings with the actual credentials from your Twilio dashboard
TWILIO_ACCOUNT_SID = 'your_account_sid_here'
TWILIO_AUTH_TOKEN = 'your_auth_token_here'
TWILIO_PHONE_NUMBER = '+1234567890' # Your Twilio provided number

# FIX 1: Changed "home" to "index" so your HTML links work perfectly
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/doctors")
def doctors():
    return render_template("doctors.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get data from your HTML form
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone") # Capturing the phone number
        password = request.form.get("password")

        # Generate a random Patient ID
        patient_id = f"PAT-{random.randint(10000, 99999)}"

        print(f"User Registered: {name}, Email: {email}, Phone: {phone}, ID: {patient_id}")

        # --- SEND SMS VIA TWILIO ---
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Welcome to DocAppointment, {name}! Your official Patient ID is: {patient_id}. You can use this to book appointments.",
                from_=TWILIO_PHONE_NUMBER,
                to=phone # The number the user typed in the form
            )
            print("SMS Sent successfully!")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

        return redirect("/")

    return render_template("register.html")

@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    if request.method == "POST":
        # FIX 2: Updated these to match the exact 'name' attributes in appointment.html
        patient_id = request.form.get("patient_id") 
        doctor = request.form.get("doctor")
        date = request.form.get("date")
        time = request.form.get("time") # Added time since it's in your form

        print("Appointment:", patient_id, doctor, date, time)
        return redirect("/")

    return render_template("appointment.html")

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)
