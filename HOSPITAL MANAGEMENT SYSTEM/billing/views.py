from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.views import View

from accounts.mixins import AdminOrReceptionistRequiredMixin
from .models import Invoice
from .forms import InvoiceForm


class InvoiceListView(AdminOrReceptionistRequiredMixin, View):
    def get(self, request):
        invoices = Invoice.objects.select_related("patient").all()
        status = request.GET.get("status")
        if status:
            invoices = invoices.filter(status=status)
        paginator = Paginator(invoices, getattr(settings, "PAGE_SIZE", 10))
        page_obj = paginator.get_page(request.GET.get("page"))
        return render(request, "billing/invoice_list.html", {"page_obj": page_obj, "status": status})


class InvoiceDetailView(AdminOrReceptionistRequiredMixin, View):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice.objects.select_related("patient", "appointment__doctor__user"), pk=pk)
        return render(request, "billing/invoice_detail.html", {"invoice": invoice})


class InvoiceCreateView(AdminOrReceptionistRequiredMixin, View):
    def get(self, request):
        return render(request, "billing/invoice_form.html", {"form": InvoiceForm(), "title": "Create Invoice"})

    def post(self, request):
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, "Invoice created successfully.")
            return redirect("billing:detail", pk=invoice.pk)
        return render(request, "billing/invoice_form.html", {"form": form, "title": "Create Invoice"})


class InvoiceUpdateView(AdminOrReceptionistRequiredMixin, View):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        return render(request, "billing/invoice_form.html", {"form": InvoiceForm(instance=invoice), "title": "Edit Invoice"})

    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, "Invoice updated successfully.")
            return redirect("billing:detail", pk=invoice.pk)
        return render(request, "billing/invoice_form.html", {"form": form, "title": "Edit Invoice"})


class InvoiceDeleteView(AdminOrReceptionistRequiredMixin, View):
    def post(self, request, pk):
        get_object_or_404(Invoice, pk=pk).delete()
        messages.success(request, "Invoice deleted.")
        return redirect("billing:list")
