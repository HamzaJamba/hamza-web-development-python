from django import forms
from .models import Patient, MedicalHistory


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "full_name", "age", "gender", "phone", "address",
            "blood_group", "emergency_contact", "photo", "is_active",
        ]


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ["patient", "doctor", "diagnosis", "notes", "attachment"]


class PatientFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    gender = forms.ChoiceField(choices=[("", "All")] + list(Patient.Gender.choices), required=False)
