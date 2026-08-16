from django import forms
from .models import Appointment
from doctors.models import Doctor
from patients.models import Patient


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "time", "reason", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True)
        self.fields["patient"].queryset = Patient.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")
        if doctor and date and time:
            clashing = Appointment.objects.filter(doctor=doctor, date=date, time=time)
            if self.instance and self.instance.pk:
                clashing = clashing.exclude(pk=self.instance.pk)
            if clashing.exists():
                raise forms.ValidationError("This doctor already has an appointment at that date and time.")
        return cleaned_data


class AppointmentFilterForm(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)
    status = forms.ChoiceField(choices=[("", "All")] + list(Appointment.Status.choices), required=False)
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
