import datetime
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from doctors.models import Doctor
from patients.models import Patient, MedicalHistory
from appointments.models import Appointment
from billing.models import Invoice
from prescriptions.models import Prescription, Medicine


class Command(BaseCommand):
    help = "Seeds the database with demo Hospital Management System data."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"first_name": "Hamza", "last_name": "Admin", "email": "admin@hms.local", "role": User.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        admin.set_password("admin123")
        admin.save()

        receptionist, _ = User.objects.get_or_create(
            username="reception1",
            defaults={"first_name": "Ayesha", "last_name": "Khan", "email": "reception1@hms.local", "role": User.Role.RECEPTIONIST},
        )
        receptionist.set_password("reception123")
        receptionist.save()

        doctor_data = [
            ("dr.ali", "Ali", "Raza", "Cardiology", "MBBS, FCPS (Cardiology)", 3000),
            ("dr.sara", "Sara", "Ahmed", "Dermatology", "MBBS, FCPS (Dermatology)", 2500),
            ("dr.usman", "Usman", "Tariq", "Orthopedics", "MBBS, MS (Orthopedics)", 3500),
        ]
        doctors = []
        for username, fn, ln, spec, qual, fee in doctor_data:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"first_name": fn, "last_name": ln, "email": f"{username}@hms.local", "role": User.Role.DOCTOR},
            )
            user.set_password("doctor123")
            user.save()
            doctor, _ = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    "employee_id": f"DOC-{len(doctors) + 1:03d}", "specialization": spec, "qualification": qual,
                    "phone": "0300" + str(1000000 + len(doctors)), "consultation_fee": fee,
                    "available_days": "Mon, Wed, Fri", "is_active": True,
                },
            )
            doctors.append(doctor)

        patient_names = [
            ("Bilal Hussain", 34, "MALE"), ("Fatima Noor", 28, "FEMALE"), ("Hamza Sheikh", 45, "MALE"),
            ("Zainab Malik", 19, "FEMALE"), ("Ahmed Iqbal", 52, "MALE"), ("Mahnoor Fareed", 8, "FEMALE"),
            ("Kashif Javed", 61, "MALE"), ("Sana Yousaf", 37, "FEMALE"),
        ]
        blood_groups = ["A+", "B+", "O+", "AB+", "A-", "O-"]
        patients = []
        for i, (name, age, gender) in enumerate(patient_names):
            patient, _ = Patient.objects.get_or_create(
                full_name=name,
                defaults={
                    "age": age, "gender": gender, "phone": f"0301{2000000 + i}",
                    "address": "Lahore, Pakistan", "blood_group": random.choice(blood_groups),
                    "emergency_contact": f"0302{3000000 + i}", "registered_by": receptionist, "is_active": True,
                },
            )
            patients.append(patient)

        today = datetime.date.today()
        statuses = ["SCHEDULED", "COMPLETED", "COMPLETED", "CANCELLED"]
        for i, patient in enumerate(patients):
            doctor = doctors[i % len(doctors)]
            for d in range(2):
                appt_date = today - datetime.timedelta(days=d * 3)
                appt_time = datetime.time(9 + (i % 6), 0)
                status = statuses[(i + d) % len(statuses)]
                appointment, _ = Appointment.objects.get_or_create(
                    doctor=doctor, date=appt_date, time=appt_time,
                    defaults={"patient": patient, "reason": "General checkup", "status": status, "created_by": receptionist},
                )

                if status == "COMPLETED":
                    MedicalHistory.objects.get_or_create(
                        patient=patient, doctor=doctor, diagnosis="Routine checkup - stable",
                        defaults={"notes": "No major concerns. Advised follow-up in 2 weeks."},
                    )

                    invoice, created = Invoice.objects.get_or_create(
                        appointment=appointment,
                        defaults={
                            "patient": patient, "consultation_fee": doctor.consultation_fee,
                            "other_charges": random.choice([0, 500, 1200]),
                            "amount_paid": doctor.consultation_fee, "status": "PAID",
                        },
                    )

                    prescription, created = Prescription.objects.get_or_create(
                        appointment=appointment,
                        defaults={
                            "patient": patient, "doctor": doctor, "diagnosis": "Routine checkup - stable",
                            "notes": "Continue current lifestyle. Stay hydrated.",
                            "follow_up_date": appt_date + datetime.timedelta(days=14),
                        },
                    )
                    if created:
                        Medicine.objects.create(prescription=prescription, name="Paracetamol", dosage="1-0-1", duration="3 days", instructions="After meal")
                        Medicine.objects.create(prescription=prescription, name="Vitamin C", dosage="1-0-0", duration="10 days", instructions="Morning")

        # A couple of pending/partial invoices for variety
        for patient in patients[:3]:
            Invoice.objects.get_or_create(
                patient=patient, consultation_fee=2000, other_charges=800,
                defaults={"amount_paid": 1000, "status": "PARTIAL", "notes": "Lab tests pending payment."},
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded!"))
        self.stdout.write("  Admin        -> username: admin        password: admin123")
        self.stdout.write("  Receptionist -> username: reception1   password: reception123")
        self.stdout.write("  Doctors      -> username: dr.ali / dr.sara / dr.usman   password: doctor123")
