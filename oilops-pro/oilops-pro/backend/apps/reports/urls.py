from django.urls import path

from .views import ReportListView, ReportView

urlpatterns = [
    path("", ReportListView.as_view()),
    path("<str:name>/", ReportView.as_view()),
]
