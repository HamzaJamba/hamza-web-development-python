from django import forms
from .models import Invoice


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["patient", "appointment", "consultation_fee", "other_charges", "amount_paid", "status", "notes"]
