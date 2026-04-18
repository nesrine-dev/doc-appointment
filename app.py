from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "docappointment-secret-2026")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///docappointment.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


#  MODELS

class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone         = db.Column(db.String(20))
    dob           = db.Column(db.String(20))
    gender        = db.Column(db.String(10))
    role          = db.Column(db.String(10), default="patient")
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    appointments   = db.relationship("Appointment", foreign_keys="Appointment.patient_id", backref="patient", lazy=True)
    doctor_profile = db.relationship("Doctor", backref="user", uselist=False, lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Doctor(db.Model):
    __tablename__ = "doctors"
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    specialty      = db.Column(db.String(100), nullable=False)
    bio            = db.Column(db.Text, default="")
    available_days = db.Column(db.String(100), default="Mon,Tue,Wed,Thu,Fri")
    image_url      = db.Column(db.String(255), default="")

    appointments   = db.relationship("Appointment", foreign_keys="Appointment.doctor_id", backref="doctor", lazy=True)


class Appointment(db.Model):
    __tablename__ = "appointments"
    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id  = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appt_date  = db.Column(db.String(20), nullable=False)
    appt_time  = db.Column(db.String(10), nullable=False)
    status     = db.Column(db.String(20), default="pending")
    notes      = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoice    = db.relationship("Invoice", backref="appointment", uselist=False, lazy=True)


class Invoice(db.Model):
    __tablename__ = "invoices"
    id             = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    treatment      = db.Column(db.String(200), default="General Consultation")
    medicines      = db.Column(db.String(300), default="")
    consultation   = db.Column(db.Float, default=0.0)
    medicine_cost  = db.Column(db.Float, default=0.0)
    total_cost     = db.Column(db.Float, default=0.0)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)


#  AUTH DECORATORS


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") not in ("doctor", "admin"):
            flash("Doctor access required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

#  PUBLIC ROUTES

@app.route("/")
def index():
    doctors = Doctor.query.join(User).all()
    return render_template("index.html", doctors=doctors)

@app.route("/doctors")
def doctors():
    all_doctors = Doctor.query.join(User).all()
    return render_template("doctors.html", doctors=all_doctors)

@app.route("/schedule")
def schedule():
    return render_template("schedule.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Your message has been received! We will respond within 24 hours.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

#  AUTH ROUTES

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone    = request.form.get("phone", "")
        dob      = request.form.get("dob", "")
        gender   = request.form.get("gender", "")

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("register"))

        user = User(name=name, email=email, phone=phone, dob=dob, gender=gender, role="patient")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user_id"]   = user.id
        session["user_name"] = user.name
        session["role"]      = user.role
        flash(f"Welcome, {user.name}! Your account has been created.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user     = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"]   = user.id
            session["user_name"] = user.name
            session["role"]      = user.role
            flash(f"Welcome back, {user.name}!", "success")
            if user.role == "admin":
                return redirect(url_for("admin"))
            elif user.role == "doctor":
                return redirect(url_for("doctor_dashboard"))
            else:
                return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

#  PATIENT ROUTES

@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    appointments = Appointment.query.filter_by(patient_id=user.id)\
                    .order_by(Appointment.appt_date.desc()).all()
    return render_template("dashboard.html", user=user, appointments=appointments)


@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
    doctors_list = Doctor.query.join(User).all()
    if request.method == "POST":
        doctor_id = request.form.get("doctor")
        appt_date = request.form.get("date")
        appt_time = request.form.get("time")

        try:
            chosen = datetime.strptime(appt_date, "%Y-%m-%d").date()
            if chosen < date.today():
                flash("Please select a future date.", "danger")
                return redirect(url_for("appointment"))
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for("appointment"))

        conflict = Appointment.query.filter_by(
            doctor_id=doctor_id, appt_date=appt_date, appt_time=appt_time
        ).filter(Appointment.status != "cancelled").first()
        if conflict:
            flash("That time slot is already booked. Please choose another.", "danger")
            return redirect(url_for("appointment"))

        appt = Appointment(
            patient_id=session["user_id"],
            doctor_id=int(doctor_id),
            appt_date=appt_date,
            appt_time=appt_time,
            status="pending"
        )
        db.session.add(appt)
        db.session.commit()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("appointment.html", doctors=doctors_list)


@app.route("/appointment/cancel/<int:appt_id>", methods=["POST"])
@login_required
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != session["user_id"] and session.get("role") != "admin":
        flash("Not authorized.", "danger")
        return redirect(url_for("dashboard"))
    appt.status = "cancelled"
    db.session.commit()
    flash("Appointment cancelled.", "info")
    return redirect(url_for("dashboard"))

#  INVOICE

@app.route("/invoice/<int:appt_id>")
@login_required
def invoice(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if session["user_id"] != appt.patient_id and session.get("role") not in ("admin", "doctor"):
        flash("Not authorized.", "danger")
        return redirect(url_for("dashboard"))
    inv = appt.invoice
    return render_template("invoice.html", appointment=appt, invoice=inv)

#  DOCTOR ROUTES

@app.route("/doctor/dashboard")
@login_required
@doctor_required
def doctor_dashboard():
    user   = User.query.get(session["user_id"])
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    appointments = []
    if doctor:
        appointments = Appointment.query.filter_by(doctor_id=doctor.id)\
                        .order_by(Appointment.appt_date.asc()).all()
    return render_template("doctor_dashboard.html", user=user, doctor=doctor, appointments=appointments)


@app.route("/doctor/appointment/<int:appt_id>/status", methods=["POST"])
@login_required
@doctor_required
def update_appointment_status(appt_id):
    appt       = Appointment.query.get_or_404(appt_id)
    new_status = request.form.get("status")
    appt.status = new_status
    db.session.commit()

    if new_status == "completed" and not appt.invoice:
        treatment     = request.form.get("treatment", "General Consultation")
        medicines     = request.form.get("medicines", "")
        consultation  = float(request.form.get("consultation", 200.0))
        medicine_cost = float(request.form.get("medicine_cost", 0.0))
        inv = Invoice(
            appointment_id=appt_id,
            treatment=treatment,
            medicines=medicines,
            consultation=consultation,
            medicine_cost=medicine_cost,
            total_cost=consultation + medicine_cost
        )
        db.session.add(inv)
        db.session.commit()
        flash("Appointment completed and invoice generated.", "success")
    else:
        flash(f"Status updated to '{new_status}'.", "success")
    return redirect(url_for("doctor_dashboard"))

#  ADMIN ROUTES

@app.route("/admin")
@login_required
@admin_required
def admin():
    users        = User.query.order_by(User.created_at.desc()).all()
    all_doctors  = Doctor.query.join(User).all()
    appointments = Appointment.query.order_by(Appointment.appt_date.desc()).all()
    invoices     = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template("admin.html", users=users, doctors=all_doctors,
                           appointments=appointments, invoices=invoices)


@app.route("/admin/appointment/<int:appt_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.invoice:
        db.session.delete(appt.invoice)
    db.session.delete(appt)
    db.session.commit()
    flash("Appointment deleted.", "info")
    return redirect(url_for("admin"))


@app.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", "info")
    return redirect(url_for("admin"))


@app.route("/admin/doctor/add", methods=["POST"])
@login_required
@admin_required
def admin_add_doctor():
    email     = request.form.get("email", "").strip().lower()
    name      = request.form.get("name", "").strip()
    specialty = request.form.get("specialty", "")
    bio       = request.form.get("bio", "")
    password  = request.form.get("password", "DocPass2026!")

    existing = User.query.filter_by(email=email).first()
    if existing:
        user = existing
        user.role = "doctor"
    else:
        user = User(name=name, email=email, role="doctor")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

    doctor = Doctor(user_id=user.id, specialty=specialty, bio=bio)
    db.session.add(doctor)
    db.session.commit()
    flash(f"Dr. {name} added successfully.", "success")
    return redirect(url_for("admin"))

#  INIT DB

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
