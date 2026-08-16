from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from django.db.models import Sum

from doctors.models import Doctor
from patients.models import Patient
from appointments.models import Appointment
from billing.models import Invoice
from prescriptions.models import Prescription


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        today = timezone.localdate()

        if user.role == "ADMIN":
            context = {
                "total_doctors": Doctor.objects.filter(is_active=True).count(),
                "total_patients": Patient.objects.filter(is_active=True).count(),
                "today_appointments": Appointment.objects.filter(date=today).count(),
                "total_revenue": Invoice.objects.aggregate(total=Sum("amount_paid"))["total"] or 0,
                "pending_bills": Invoice.objects.exclude(status="PAID").count(),
                "recent_appointments": Appointment.objects.select_related("patient", "doctor__user").order_by("-created_at")[:6],
            }
            template = "dashboard/admin_dashboard.html"

        elif user.role == "DOCTOR":
            doctor = getattr(user, "doctor_profile", None)
            appointments = Appointment.objects.filter(doctor=doctor) if doctor else Appointment.objects.none()
            context = {
                "doctor": doctor,
                "today_appointments": appointments.filter(date=today).order_by("time"),
                "upcoming_count": appointments.filter(status="SCHEDULED").count(),
                "completed_count": appointments.filter(status="COMPLETED").count(),
                "recent_prescriptions": Prescription.objects.filter(doctor=doctor).order_by("-date")[:6] if doctor else [],
            }
            template = "dashboard/doctor_dashboard.html"

        else:  # RECEPTIONIST
            context = {
                "today_appointments": Appointment.objects.filter(date=today).select_related("patient", "doctor__user").order_by("time"),
                "total_patients": Patient.objects.filter(is_active=True).count(),
                "pending_bills": Invoice.objects.exclude(status="PAID").count(),
                "recent_patients": Patient.objects.order_by("-registered_date")[:6],
            }
            template = "dashboard/receptionist_dashboard.html"

        return render(request, template, context)
