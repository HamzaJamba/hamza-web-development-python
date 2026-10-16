from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.audit.mixins import AuditMixin
from apps.audit.services import log_action

from .models import Incident, IncidentAttachment
from .serializers import AttachmentSerializer, IncidentDetailSerializer, IncidentSerializer
from .services import handle_new_incident

REPORTERS = [r for r in Role.values if r != Role.VIEWER]
INVESTIGATORS = [Role.SAFETY_OFFICER, Role.PLANT_MANAGER, Role.ENGINEER]


class IncidentViewSet(AuditMixin, viewsets.ModelViewSet):
    write_roles = INVESTIGATORS
    action_roles = {"create": REPORTERS, "attachments": REPORTERS}
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filterset_fields = ["incident_type", "severity", "status", "plant", "equipment"]
    search_fields = ["number", "title", "description"]
    ordering_fields = ["occurred_at", "severity", "estimated_loss"]

    def get_queryset(self):
        return Incident.objects.select_related("plant", "equipment", "reported_by").prefetch_related("attachments")

    def get_serializer_class(self):
        return IncidentDetailSerializer if self.action == "retrieve" else IncidentSerializer

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
        incident = serializer.instance
        log_action(self.request.user, "CREATE", "Incident", incident.pk, incident, request=self.request)
        handle_new_incident(incident)

    def perform_update(self, serializer):
        closing = serializer.validated_data.get("status") in ("RESOLVED", "CLOSED")
        super().perform_update(serializer)
        inc = serializer.instance
        if closing and not inc.closed_at:
            inc.closed_at = timezone.now()
            inc.save(update_fields=["closed_at"])

    @extend_schema(request=AttachmentSerializer, responses=AttachmentSerializer(many=True))
    @action(detail=True, methods=["get", "post"], parser_classes=[MultiPartParser, FormParser])
    def attachments(self, request, pk=None):
        incident = self.get_object()
        if request.method == "GET":
            return Response(AttachmentSerializer(incident.attachments.all(), many=True, context={"request": request}).data)
        s = AttachmentSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        s.save(incident=incident, uploaded_by=request.user)
        log_action(request.user, "UPLOAD", "Incident", incident.pk, incident, {"file": s.instance.file.name}, request)
        return Response(s.data, status=status.HTTP_201_CREATED)


class AttachmentViewSet(AuditMixin, viewsets.GenericViewSet, viewsets.mixins.DestroyModelMixin):
    queryset = IncidentAttachment.objects.all()
    serializer_class = AttachmentSerializer
    write_roles = INVESTIGATORS
