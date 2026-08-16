from django import forms
from django.forms import inlineformset_factory
from .models import Prescription, Medicine


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["patient", "doctor", "appointment", "diagnosis", "notes", "follow_up_date"]
        widgets = {"follow_up_date": forms.DateInput(attrs={"type": "date"})}


MedicineFormSet = inlineformset_factory(
    Prescription, Medicine,
    fields=["name", "dosage", "duration", "instructions"],
    extra=3, can_delete=True,
)
