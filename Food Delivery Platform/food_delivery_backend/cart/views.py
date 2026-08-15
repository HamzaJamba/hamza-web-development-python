from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsCustomer
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer


class CartView(APIView):
    """GET /api/cart/  -> the logged-in customer's cart (creates an empty one if none exists)."""

    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        """Clear the whole cart."""
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        cart.items.all().delete()
        cart.restaurant = None
        cart.save(update_fields=["restaurant"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddCartItemView(APIView):
    """POST /api/cart/items/  {food_item_id, quantity, special_instructions, replace_cart}"""

    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """PATCH /api/cart/items/{id}/  {quantity}   |   DELETE /api/cart/items/{id}/"""

    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_object(self, request, pk):
        return CartItem.objects.get(id=pk, cart__customer=request.user)

    def patch(self, request, pk):
        item = self.get_object(request, pk)
        quantity = request.data.get("quantity")
        if not quantity or int(quantity) < 1:
            return Response({"quantity": "Must be >= 1. Use DELETE to remove."}, status=status.HTTP_400_BAD_REQUEST)
        item.quantity = int(quantity)
        item.save(update_fields=["quantity"])
        return Response(CartSerializer(item.cart).data)

    def delete(self, request, pk):
        item = self.get_object(request, pk)
        cart = item.cart
        item.delete()
        if not cart.items.exists():
            cart.restaurant = None
            cart.save(update_fields=["restaurant"])
        return Response(CartSerializer(cart).data)
