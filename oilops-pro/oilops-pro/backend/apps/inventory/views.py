from django.db.models import F
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.audit.mixins import AuditMixin

from .models import Item, StockMovement
from .serializers import AdjustSerializer, ItemSerializer, StockMovementSerializer
from .services import adjust_stock

STORE = [Role.STORE_KEEPER, Role.PLANT_MANAGER]


class ItemViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Item.objects.select_related("plant")
    serializer_class = ItemSerializer
    write_roles = STORE
    action_roles = {"adjust": STORE + [Role.ENGINEER]}
    filterset_fields = ["category", "plant", "is_active"]
    search_fields = ["sku", "name", "supplier"]
    ordering_fields = ["name", "quantity", "unit_cost"]

    @action(detail=False, methods=["get"], url_path="low-stock", pagination_class=None)
    def low_stock(self, request):
        qs = self.filter_queryset(self.get_queryset()).filter(is_active=True, quantity__lte=F("reorder_level"))
        return Response(self.get_serializer(qs, many=True).data)

    @extend_schema(request=AdjustSerializer, responses=StockMovementSerializer)
    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        item = self.get_object()
        s = AdjustSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        m = adjust_stock(item.pk, user=request.user, **s.validated_data)
        return Response(StockMovementSerializer(m).data, status=201)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.select_related("item", "performed_by")
    serializer_class = StockMovementSerializer
    filterset_fields = ["item", "movement_type", "item__category"]
    search_fields = ["reference", "item__name", "item__sku"]
