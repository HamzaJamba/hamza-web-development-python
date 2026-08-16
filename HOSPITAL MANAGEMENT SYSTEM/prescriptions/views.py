from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.views import View

from accounts.mixins import DoctorRequiredMixin, StaffRequiredMixin
from .models import Prescription
from .forms import PrescriptionForm, MedicineFormSet


class PrescriptionListView(StaffRequiredMixin, View):
    def get(self, request):
        prescriptions = Prescription.objects.select_related("patient", "doctor__user").all()
        user = request.user
        if user.role == "DOCTOR":
            prescriptions = prescriptions.filter(doctor__user=user)
        paginator = Paginator(prescriptions, getattr(settings, "PAGE_SIZE", 10))
        page_obj = paginator.get_page(request.GET.get("page"))
        return render(request, "prescriptions/prescription_list.html", {"page_obj": page_obj})


class PrescriptionDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        prescription = get_object_or_404(Prescription.objects.select_related("patient", "doctor__user"), pk=pk)
        return render(request, "prescriptions/prescription_detail.html", {"prescription": prescription})


class PrescriptionCreateView(DoctorRequiredMixin, View):
    def get(self, request):
        form = PrescriptionForm()
        formset = MedicineFormSet()
        return render(request, "prescriptions/prescription_form.html", {"form": form, "formset": formset, "title": "New Prescription"})

    def post(self, request):
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            formset = MedicineFormSet(request.POST, instance=prescription)
            prescription.save()
            formset.instance = prescription
            if formset.is_valid():
                formset.save()
                messages.success(request, "Prescription created successfully.")
                return redirect("prescriptions:detail", pk=prescription.pk)
        else:
            formset = MedicineFormSet(request.POST)
        return render(request, "prescriptions/prescription_form.html", {"form": form, "formset": formset, "title": "New Prescription"})


class PrescriptionUpdateView(DoctorRequiredMixin, View):
    def get(self, request, pk):
        prescription = get_object_or_404(Prescription, pk=pk)
        form = PrescriptionForm(instance=prescription)
        formset = MedicineFormSet(instance=prescription)
        return render(request, "prescriptions/prescription_form.html", {"form": form, "formset": formset, "title": "Edit Prescription"})

    def post(self, request, pk):
        prescription = get_object_or_404(Prescription, pk=pk)
        form = PrescriptionForm(request.POST, instance=prescription)
        formset = MedicineFormSet(request.POST, instance=prescription)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Prescription updated successfully.")
            return redirect("prescriptions:detail", pk=prescription.pk)
        return render(request, "prescriptions/prescription_form.html", {"form": form, "formset": formset, "title": "Edit Prescription"})


class PrescriptionDeleteView(DoctorRequiredMixin, View):
    def post(self, request, pk):
        get_object_or_404(Prescription, pk=pk).delete()
        messages.success(request, "Prescription deleted.")
        return redirect("prescriptions:list")
