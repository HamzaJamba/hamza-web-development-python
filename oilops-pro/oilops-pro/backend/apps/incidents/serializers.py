import os

from django.conf import settings
from rest_framework import serializers

from .models import Incident, IncidentAttachment

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"}


class AttachmentSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = IncidentAttachment
        fields = ["id", "incident", "file", "file_name", "kind", "description", "uploaded_by", "uploaded_at"]
        read_only_fields = ["incident", "kind", "uploaded_by", "uploaded_at"]

    def get_file_name(self, obj) -> str:
        return os.path.basename(obj.file.name)

    def validate_file(self, f):
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in PHOTO_EXT | DOC_EXT:
            raise serializers.ValidationError(f"File type {ext or '(none)'} is not allowed.")
        if f.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
            raise serializers.ValidationError(f"File exceeds {settings.MAX_UPLOAD_MB} MB.")
        return f

    def create(self, validated_data):
        ext = os.path.splitext(validated_data["file"].name)[1].lower()
        validated_data["kind"] = "PHOTO" if ext in PHOTO_EXT else "DOCUMENT"
        return super().create(validated_data)


class IncidentSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(source="plant.name", read_only=True)
    equipment_name = serializers.CharField(source="equipment.name", read_only=True, default="")
    reporter_name = serializers.CharField(source="reported_by.full_name", read_only=True, default="")
    attachment_count = serializers.IntegerField(source="attachments.count", read_only=True)

    class Meta:
        model = Incident
        fields = "__all__"
        read_only_fields = ["number", "reported_by", "closed_at"]

    def validate(self, attrs):
        g = lambda k: attrs.get(k, getattr(self.instance, k, None))  # noqa: E731
        eq, plant = g("equipment"), g("plant")
        if eq and plant and eq.plant_id != plant.pk:
            raise serializers.ValidationError({"equipment": "Equipment does not belong to the selected plant."})
        if g("status") in ("RESOLVED", "CLOSED"):
            missing = [f for f in ("root_cause", "corrective_action") if not g(f)]
            if missing:
                raise serializers.ValidationError({f: "Required before resolving or closing." for f in missing})
        return attrs


class IncidentDetailSerializer(IncidentSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
