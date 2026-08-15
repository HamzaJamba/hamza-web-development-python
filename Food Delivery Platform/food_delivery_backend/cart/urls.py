from django.urls import path
from .views import CartView, AddCartItemView, CartItemDetailView

urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("items/", AddCartItemView.as_view(), name="cart-add-item"),
    path("items/<uuid:pk>/", CartItemDetailView.as_view(), name="cart-item-detail"),
]
