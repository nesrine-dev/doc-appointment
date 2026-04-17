"""
Run once to populate the database with sample data.
Usage: python seed.py
"""
from app import app, db, User, Doctor, Appointment, Invoice
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    db.drop_all()
    db.create_all()

    # ── ADMIN ────────────────────────────────────────
    admin = User(name="Admin User", email="admin@docappointment.com",
                 phone="+90 555 000 001", gender="male", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)

    # ── DOCTORS ─────────────────────────────────────
    doctor_data = [
        ("Sarah Ahmed",   "sarah@docappointment.com",   "Cardiology",       "15+ years in interventional cardiology. Trained at Istanbul University Medical School."),
        ("Michael Lee",   "michael@docappointment.com", "Neurology",        "Specialist in neurological disorders and brain health. Published researcher."),
        ("Emily Smith",   "emily@docappointment.com",   "Dermatology",      "Expert in skin conditions, cosmetic dermatology, and laser treatments."),
        ("David Kim",     "david@docappointment.com",   "Pediatrics",       "Dedicated to children's health with a warm, family-friendly approach."),
        ("Ahmet Yilmaz",  "ahmet@docappointment.com",   "General Practice", "Experienced general practitioner serving patients of all ages."),
        ("Elif Kaya",     "elif@docappointment.com",    "Orthopedics",      "Sports medicine specialist focusing on joint and bone health."),
    ]
    doctor_users = []
    for name, email, specialty, bio in doctor_data:
        u = User(name=name, email=email, phone="+90 555 100 00" + str(len(doctor_users)+1),
                 gender="female" if name in ("Sarah Ahmed","Emily Smith","Elif Kaya") else "male",
                 role="doctor")
        u.set_password("doctor123")
        db.session.add(u)
        db.session.flush()
        d = Doctor(user_id=u.id, specialty=specialty, bio=bio, available_days="Mon,Tue,Wed,Thu,Fri")
        db.session.add(d)
        db.session.flush()
        doctor_users.append((u, d))

    # ── PATIENTS ────────────────────────────────────
    patient_data = [
        ("Ali Demir",       "ali@example.com",    "+90 555 200 001", "1990-03-14", "male"),
        ("Zeynep Sahin",    "zeynep@example.com", "+90 555 200 002", "1995-07-22", "female"),
        ("Mehmet Can",      "mehmet@example.com", "+90 555 200 003", "1985-11-08", "male"),
        ("Fatma Ozturk",    "fatma@example.com",  "+90 555 200 004", "1992-01-30", "female"),
        ("Burak Arslan",    "burak@example.com",  "+90 555 200 005", "1988-05-17", "male"),
        ("Selin Yildiz",    "selin@example.com",  "+90 555 200 006", "2000-09-05", "female"),
        ("Kemal Aydin",     "kemal@example.com",  "+90 555 200 007", "1975-12-19", "male"),
        ("Aysegul Celik",   "aysegul@example.com","+90 555 200 008", "1998-04-11", "female"),
        ("Hasan Koc",       "hasan@example.com",  "+90 555 200 009", "1982-06-28", "male"),
        ("Merve Polat",     "merve@example.com",  "+90 555 200 010", "1997-02-15", "female"),
    ]
    patients = []
    for name, email, phone, dob, gender in patient_data:
        p = User(name=name, email=email, phone=phone, dob=dob, gender=gender, role="patient")
        p.set_password("patient123")
        db.session.add(p)
        db.session.flush()
        patients.append(p)

    # ── APPOINTMENTS & INVOICES ──────────────────────
    appt_data = [
        (patients[0], doctor_users[0][1], "2026-04-20", "09:00", "completed"),
        (patients[1], doctor_users[1][1], "2026-04-21", "10:30", "confirmed"),
        (patients[2], doctor_users[2][1], "2026-04-22", "11:00", "pending"),
        (patients[3], doctor_users[3][1], "2026-04-23", "14:00", "confirmed"),
        (patients[4], doctor_users[4][1], "2026-04-24", "09:30", "completed"),
        (patients[5], doctor_users[5][1], "2026-04-25", "15:00", "pending"),
        (patients[6], doctor_users[0][1], "2026-04-28", "08:00", "confirmed"),
        (patients[7], doctor_users[2][1], "2026-05-02", "13:00", "pending"),
        (patients[8], doctor_users[1][1], "2026-05-05", "10:00", "pending"),
        (patients[9], doctor_users[3][1], "2026-05-08", "11:30", "confirmed"),
        (patients[0], doctor_users[4][1], "2026-03-15", "09:00", "completed"),
        (patients[1], doctor_users[5][1], "2026-03-20", "14:00", "completed"),
    ]
    appts = []
    for patient, doctor, d, t, status in appt_data:
        a = Appointment(patient_id=patient.id, doctor_id=doctor.id,
                        appt_date=d, appt_time=t, status=status)
        db.session.add(a)
        db.session.flush()
        appts.append(a)

    # Invoices for completed appointments
    invoice_data = [
        (appts[0],  "ECG & Cardio Evaluation",        "Aspirin 100mg, Bisoprolol 5mg", 350.0, 120.0),
        (appts[4],  "Routine Health Checkup",          "Vitamin D, Multivitamin",        200.0,  45.0),
        (appts[10], "Follow-up Cardiology Consult",    "Beta-blocker refill",            250.0,  80.0),
        (appts[11], "Knee Joint Assessment",           "Ibuprofen 400mg, Gel cream",     300.0,  60.0),
    ]
    for appt, treatment, medicines, consult, med_cost in invoice_data:
        inv = Invoice(
            appointment_id=appt.id,
            treatment=treatment,
            medicines=medicines,
            consultation=consult,
            medicine_cost=med_cost,
            total_cost=consult + med_cost
        )
        db.session.add(inv)

    db.session.commit()
    print("Database seeded successfully!")
    print("─────────────────────────────────────────")
    print("Admin login:   admin@docappointment.com  / admin123")
    print("Doctor login:  sarah@docappointment.com  / doctor123")
    print("Patient login: ali@example.com           / patient123")
    print("─────────────────────────────────────────")
