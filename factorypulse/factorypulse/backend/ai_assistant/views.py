from django.core.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from equipment.models import Machine
from .services import explain_machine


class AskAssistantView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "ai_assistant"

    def post(self, request):
        machine_id = request.data.get("machine_id")
        question = request.data.get("question", "")
        try:
            machine = Machine.objects.get(pk=machine_id)
        except (Machine.DoesNotExist, ValueError, TypeError, ValidationError):
            return Response({"detail": "Valid machine_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        result = explain_machine(machine, question)
        return Response(result)
