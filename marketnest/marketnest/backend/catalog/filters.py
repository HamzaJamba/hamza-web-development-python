import django_filters as df
from .models import Product


class ProductFilter(df.FilterSet):
    category = df.CharFilter(field_name="category__slug")
    vendor = df.CharFilter(field_name="vendor__slug")
    min_price = df.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = df.NumberFilter(field_name="price", lookup_expr="lte")
    on_sale = df.BooleanFilter(method="filter_on_sale")
    in_stock = df.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "vendor", "min_price", "max_price", "on_sale", "in_stock"]

    def filter_on_sale(self, qs, name, value):
        return qs.filter(compare_at_price__isnull=False) if value else qs

    def filter_in_stock(self, qs, name, value):
        return qs.filter(stock__gt=0) if value else qs
