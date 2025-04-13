from django.db.models import Q
from rest_framework.filters import SearchFilter
from rest_framework.filters import BaseFilterBackend


class FlexibleSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('search', '').strip()

        if search_query:
            return queryset.filter(
                Q(id__icontains=search_query) |
                Q(product_variant__product__product_name__icontains=search_query) |
                Q(product_variant__product__sku__icontains=search_query) |
                Q(product_variant__product__category__category_name__icontains=search_query) |
                Q(product_variant__productbarcodes__barcode__icontains=search_query)
            ).distinct()

        return queryset

class CustomSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_param = request.query_params.get('search', None)

        if search_param:
            # Default search fields
            queryset = super().filter_queryset(request, queryset, view)

            # Add barcode search manually
            queryset = queryset.filter(
                Q(product_variant__productbarcodes__barcode__icontains=search_param)
            ).distinct()

        return queryset