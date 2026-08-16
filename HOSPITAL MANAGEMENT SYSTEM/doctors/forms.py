from django import forms
from accounts.models import User
from .models import Doctor


class DoctorForm(forms.ModelForm):
    """Creates/updates a Doctor profile. When creating, also creates the linked login account."""
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Required when creating a new doctor")

    class Meta:
        model = Doctor
        fields = [
            "employee_id", "specialization", "qualification", "phone",
            "consultation_fee", "available_days", "photo", "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["username"].initial = self.instance.user.username
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email
            self.fields["password"].help_text = "Leave blank to keep current password"

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        if not (self.instance and self.instance.pk) and not cleaned_data.get("password"):
            raise forms.ValidationError("A password is required when creating a new doctor account.")
        return cleaned_data

    def save(self, commit=True):
        doctor = super().save(commit=False)
        if doctor.pk:
            user = doctor.user
        else:
            user = User(role=User.Role.DOCTOR)

        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            doctor.user = user
            doctor.save()
        return doctor
