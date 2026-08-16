from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.views import View

from .forms import StyledAuthenticationForm, StaffCreateForm, StaffUpdateForm
from .mixins import AdminRequiredMixin
from .models import User


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


class StaffListView(AdminRequiredMixin, View):
    def get(self, request):
        q = request.GET.get("q", "")
        users = User.objects.exclude(role=User.Role.DOCTOR).order_by("username")
        if q:
            users = users.filter(username__icontains=q)
        paginator = Paginator(users, getattr(settings, "PAGE_SIZE", 10))
        page_obj = paginator.get_page(request.GET.get("page"))
        return render(request, "accounts/staff_list.html", {"page_obj": page_obj, "q": q})


class StaffCreateView(AdminRequiredMixin, View):
    def get(self, request):
        return render(request, "accounts/staff_form.html", {"form": StaffCreateForm(), "title": "Add Staff Member"})

    def post(self, request):
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member created successfully.")
            return redirect("accounts:staff_list")
        return render(request, "accounts/staff_form.html", {"form": form, "title": "Add Staff Member"})


class StaffUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, "accounts/staff_form.html", {"form": StaffUpdateForm(instance=user), "title": "Edit Staff Member"})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = StaffUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member updated successfully.")
            return redirect("accounts:staff_list")
        return render(request, "accounts/staff_form.html", {"form": form, "title": "Edit Staff Member"})


class StaffDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        get_object_or_404(User, pk=pk).delete()
        messages.success(request, "Staff member deleted.")
        return redirect("accounts:staff_list")
