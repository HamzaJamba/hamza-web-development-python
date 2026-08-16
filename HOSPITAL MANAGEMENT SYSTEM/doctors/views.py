from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.views import View

from accounts.mixins import AdminRequiredMixin, DoctorRequiredMixin
from .models import Doctor
from .forms import DoctorForm


class DoctorListView(DoctorRequiredMixin, View):
    def get(self, request):
        q = request.GET.get("q", "")
        doctors = Doctor.objects.select_related("user").all()
        if q:
            doctors = doctors.filter(user__first_name__icontains=q) | doctors.filter(specialization__icontains=q)
        paginator = Paginator(doctors, getattr(settings, "PAGE_SIZE", 10))
        page_obj = paginator.get_page(request.GET.get("page"))
        return render(request, "doctors/doctor_list.html", {"page_obj": page_obj, "q": q})


class DoctorDetailView(DoctorRequiredMixin, View):
    def get(self, request, pk):
        doctor = get_object_or_404(Doctor.objects.select_related("user"), pk=pk)
        upcoming = doctor.appointments.filter(status="SCHEDULED").order_by("date", "time")[:10]
        return render(request, "doctors/doctor_detail.html", {"doctor": doctor, "upcoming": upcoming})


class DoctorCreateView(AdminRequiredMixin, View):
    def get(self, request):
        return render(request, "doctors/doctor_form.html", {"form": DoctorForm(), "title": "Add Doctor"})

    def post(self, request):
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor added successfully.")
            return redirect("doctors:list")
        return render(request, "doctors/doctor_form.html", {"form": form, "title": "Add Doctor"})


class DoctorUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        return render(request, "doctors/doctor_form.html", {"form": DoctorForm(instance=doctor), "title": "Edit Doctor"})

    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor updated successfully.")
            return redirect("doctors:list")
        return render(request, "doctors/doctor_form.html", {"form": form, "title": "Edit Doctor"})


class DoctorDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        doctor.user.delete()  # cascades to Doctor profile
        messages.success(request, "Doctor removed.")
        return redirect("doctors:list")
