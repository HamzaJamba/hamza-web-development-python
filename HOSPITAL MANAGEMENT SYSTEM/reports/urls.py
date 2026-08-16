from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportsHomeView.as_view(), name="home"),
    path("patients/pdf/", views.PatientsReportPDFView.as_view(), name="patients_pdf"),
    path("patients/excel/", views.PatientsExcelExportView.as_view(), name="patients_excel"),
    path("appointments/pdf/", views.AppointmentsReportPDFView.as_view(), name="appointments_pdf"),
    path("appointments/excel/", views.AppointmentsExcelExportView.as_view(), name="appointments_excel"),
    path("doctor-wise/pdf/", views.DoctorWiseReportPDFView.as_view(), name="doctor_wise_pdf"),
    path("billing/pdf/", views.BillingReportPDFView.as_view(), name="billing_pdf"),
    path("billing/excel/", views.BillingExcelExportView.as_view(), name="billing_excel"),
    path("patient/<int:patient_id>/medical/pdf/", views.PatientMedicalReportPDFView.as_view(), name="patient_medical_pdf"),
]
