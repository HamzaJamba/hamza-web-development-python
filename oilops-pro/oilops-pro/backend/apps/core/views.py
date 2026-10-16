from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = []

    @extend_schema(responses=dict)
    def get(self, request):
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT 1")
            db = "ok"
        except Exception:  # pragma: no cover
            db = "error"
        return Response({"status": "ok" if db == "ok" else "degraded", "database": db})
