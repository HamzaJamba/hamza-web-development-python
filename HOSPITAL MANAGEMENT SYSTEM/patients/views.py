from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.views import View

from accounts.mixins import StaffRequiredMixin, AdminOrReceptionistRequiredMixin
from .models import Patient, MedicalHistory
from .forms import PatientForm, MedicalHistoryForm, PatientFilterForm


class PatientListView(StaffRequiredMixin, View):
    def get(self, request):
        filter_form = PatientFilterForm(request.GET)
        patients = Patient.objects.all()
        if filter_form.is_valid():
            cd = filter_form.cleaned_data
            if cd.get("q"):
                patients = patients.filter(full_name__icontains=cd["q"]) | patients.filter(patient_id__icontains=cd["q"])
            if cd.get("gender"):
                patients = patients.filter(gender=cd["gender"])
        paginator = Paginator(patients, getattr(settings, "PAGE_SIZE", 10))
        page_obj = paginator.get_page(request.GET.get("page"))
        return render(request, "patients/patient_list.html", {"page_obj": page_obj, "filter_form": filter_form})


class PatientDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        history = patient.medical_history.select_related("doctor__user").all()
        appointments = patient.appointments.select_related("doctor__user").order_by("-date", "-time")[:10]
        invoices = patient.invoices.all()[:10]
        return render(request, "patients/patient_detail.html", {
            "patient": patient, "history": history, "appointments": appointments, "invoices": invoices,
        })


class PatientCreateView(AdminOrReceptionistRequiredMixin, View):
    def get(self, request):
        return render(request, "patients/patient_form.html", {"form": PatientForm(), "title": "Register Patient"})

    def post(self, request):
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            patient.save()
            messages.success(request, "Patient registered successfully.")
            return redirect("patients:detail", pk=patient.pk)
        return render(request, "patients/patient_form.html", {"form": form, "title": "Register Patient"})


class PatientUpdateView(AdminOrReceptionistRequiredMixin, View):
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        return render(request, "patients/patient_form.html", {"form": PatientForm(instance=patient), "title": "Edit Patient"})

    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient updated successfully.")
            return redirect("patients:detail", pk=patient.pk)
        return render(request, "patients/patient_form.html", {"form": form, "title": "Edit Patient"})


class PatientDeleteView(AdminOrReceptionistRequiredMixin, View):
    def post(self, request, pk):
        get_object_or_404(Patient, pk=pk).delete()
        messages.success(request, "Patient record deleted.")
        return redirect("patients:list")


class MedicalHistoryCreateView(StaffRequiredMixin, View):
    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        form = MedicalHistoryForm(initial={"patient": patient})
        return render(request, "patients/medical_history_form.html", {"form": form, "patient": patient})

    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        form = MedicalHistoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Medical history entry added.")
            return redirect("patients:detail", pk=patient.pk)
        return render(request, "patients/medical_history_form.html", {"form": form, "patient": patient})
