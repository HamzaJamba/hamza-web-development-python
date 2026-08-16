from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User


class StyledAuthenticationForm(AuthenticationForm):
    """Just the built-in login form, kept here so the template can style it consistently."""
    pass


class StaffCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "role", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class StaffUpdateForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep current password")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "role", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("new_password"):
            user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user
