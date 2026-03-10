from flask import Flask, render_template, request, redirect

app = Flask(__name__)

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
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        print("User Registered:", name, email)
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

if __name__ == "__main__":
    app.run(debug=True)