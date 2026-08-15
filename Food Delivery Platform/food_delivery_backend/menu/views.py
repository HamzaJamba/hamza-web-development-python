import csv
import io

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsAdmin, IsCustomer, IsRestaurantOwner
from restaurants.models import Restaurant
from .models import Category, FoodItem, FoodImage, WishlistItem
from .serializers import (
    CategorySerializer,
    FoodItemListSerializer,
    FoodItemDetailSerializer,
    FoodItemWriteSerializer,
    FoodImageSerializer,
    WishlistItemSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """Admin manages the global category list; everyone can read it."""

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.AllowAny()]


class FoodItemViewSet(viewsets.ModelViewSet):
    """
    GET /api/menu/food-items/                 -> public browse (available only), filter by restaurant/category
    GET /api/menu/food-items/{id}/             -> public detail
    POST/PATCH/DELETE                          -> restaurant owner, restricted to their own restaurant
    """

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["restaurant", "category", "is_available"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "avg_rating", "total_orders", "created_at"]

    def get_queryset(self):
        qs = FoodItem.objects.select_related("restaurant", "category").prefetch_related("images")
        if self.action == "list":
            qs = qs.filter(is_available=True, restaurant__status="APPROVED")
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return FoodItemListSerializer
        if self.action in ("create", "update", "partial_update"):
            return FoodItemWriteSerializer
        return FoodItemDetailSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsRestaurantOwner()]
        return [permissions.AllowAny()]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(
        detail=False, methods=["post"], url_path="bulk-import",
        permission_classes=[permissions.IsAuthenticated, IsRestaurantOwner],
        parser_classes=[MultiPartParser],
    )
    def bulk_import(self, request):
        """
        POST /api/menu/food-items/bulk-import/
        multipart/form-data: restaurant=<uuid>, file=<csv>

        CSV columns (header row required): name,price,category,description,discount_price
        - category is matched by name (case-insensitive); created if it doesn't exist.
        - discount_price and description are optional.
        """
        restaurant_id = request.data.get("restaurant")
        csv_file = request.FILES.get("file")

        if not restaurant_id or not csv_file:
            return Response({"detail": "Both 'restaurant' and 'file' are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id, owner=request.user)
        except Restaurant.DoesNotExist:
            return Response({"detail": "Restaurant not found or not yours."}, status=status.HTTP_404_NOT_FOUND)

        try:
            decoded = csv_file.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            return Response({"detail": "Could not read file — please upload a UTF-8 encoded CSV."}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.DictReader(io.StringIO(decoded))
        required_cols = {"name", "price"}
        if not reader.fieldnames or not required_cols.issubset({f.strip().lower() for f in reader.fieldnames}):
            return Response(
                {"detail": "CSV must have at least 'name' and 'price' columns."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created, errors = [], []
        for i, row in enumerate(reader, start=2):  # row 1 is the header
            row = {k.strip().lower(): (v or "").strip() for k, v in row.items()}
            name = row.get("name")
            price = row.get("price")
            if not name or not price:
                errors.append({"row": i, "error": "Missing name or price."})
                continue
            try:
                price_val = float(price)
            except ValueError:
                errors.append({"row": i, "error": f"Invalid price '{price}'."})
                continue

            category = None
            category_name = row.get("category")
            if category_name:
                category, _ = Category.objects.get_or_create(
                    name__iexact=category_name,
                    defaults={"name": category_name, "slug": category_name.lower().replace(" ", "-")},
                )

            discount_price = row.get("discount_price") or None
            try:
                discount_val = float(discount_price) if discount_price else None
            except ValueError:
                discount_val = None

            item = FoodItem.objects.create(
                restaurant=restaurant,
                category=category,
                name=name,
                description=row.get("description", ""),
                price=price_val,
                discount_price=discount_val,
            )
            created.append({"id": item.id, "name": item.name})

        return Response({
            "created_count": len(created),
            "error_count": len(errors),
            "created": created,
            "errors": errors,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)


class FoodImageViewSet(viewsets.ModelViewSet):
    """Nested under a food item the owner controls: /api/menu/food-items/{food_item_pk}/images/"""

    serializer_class = FoodImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsRestaurantOwner]

    def get_queryset(self):
        return FoodImage.objects.filter(
            food_item_id=self.kwargs["food_item_pk"],
            food_item__restaurant__owner=self.request.user,
        )

    def perform_create(self, serializer):
        food_item = FoodItem.objects.get(
            id=self.kwargs["food_item_pk"], restaurant__owner=self.request.user
        )
        serializer.save(food_item=food_item)


class WishlistViewSet(viewsets.ModelViewSet):
    """/api/menu/wishlist/ — customer's saved favourite foods. POST {food_item} to add, DELETE {id} to remove."""

    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return WishlistItem.objects.filter(customer=self.request.user).select_related("food_item")

    def get_serializer_context(self):
        return {"request": self.request}
