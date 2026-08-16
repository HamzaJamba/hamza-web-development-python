from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.views import View
from django.utils import timezone

from accounts.mixins import StaffRequiredMixin
from .models import Appointment
from .forms import AppointmentForm, AppointmentFilterForm


class AppointmentListView(StaffRequiredMixin, View):
    def get(self, request):
        filter_form = AppointmentFilterForm(request.GET)
        appointments = Appointment.objects.select_related("patient", "doctor__user").all()

        user = request.user
        if user.role == "DOCTOR":
            appointments = appointments.filter(doctor__user=user)

        if filter_form.is_valid():
            cd = filter_form.cleaned_data
            if cd.get("doctor"):
                appointments = appointments.filter(doctor=cd["doctor"])
            if cd.get("status"):
                appointments = appointments.filter(status=cd["status"])
            if cd.get("date"):
                appointments = appointments.filter(date=cd["date"])

        paginator = Paginator(appointments, getattr(settings, "PAGE_SIZE", 10))
        page_obj = paginator.get_page(request.GET.get("page"))
        return render(request, "appointments/appointment_list.html", {
            "page_obj": page_obj, "filter_form": filter_form, "today": timezone.localdate(),
        })


class AppointmentCreateView(StaffRequiredMixin, View):
    def get(self, request):
        return render(request, "appointments/appointment_form.html", {"form": AppointmentForm(), "title": "Book Appointment"})

    def post(self, request):
        form = AppointmentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Appointment booked successfully.")
            return redirect("appointments:list")
        return render(request, "appointments/appointment_form.html", {"form": form, "title": "Book Appointment"})


class AppointmentUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(Appointment, pk=pk)
        return render(request, "appointments/appointment_form.html", {"form": AppointmentForm(instance=obj), "title": "Edit Appointment"})

    def post(self, request, pk):
        obj = get_object_or_404(Appointment, pk=pk)
        form = AppointmentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect("appointments:list")
        return render(request, "appointments/appointment_form.html", {"form": form, "title": "Edit Appointment"})


class AppointmentDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        get_object_or_404(Appointment, pk=pk).delete()
        messages.success(request, "Appointment cancelled and removed.")
        return redirect("appointments:list")
