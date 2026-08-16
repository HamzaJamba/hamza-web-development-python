from django.db import models


class Invoice(models.Model):
    class Status(models.TextChoices):
        PAID = "PAID", "Paid"
        PARTIAL = "PARTIAL", "Partial"
        UNPAID = "UNPAID", "Unpaid"

    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="invoices")
    appointment = models.ForeignKey(
        "appointments.Appointment", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices"
    )
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Tests, medicines, etc.")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNPAID)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by("id").last()
            next_id = (last.id + 1) if last else 1
            self.invoice_number = f"INV-{next_id:05d}"
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return self.consultation_fee + self.other_charges

    @property
    def balance(self):
        return self.total_amount - self.amount_paid

    def __str__(self):
        return f"{self.invoice_number} - {self.patient}"
