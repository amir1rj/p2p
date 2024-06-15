import django_filters
from .models import Product, Category, Vendor, Place, Unit, PRODUCT_TYPE_CHOICES


class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Min Price')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Max Price')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    vendor = django_filters.ModelChoiceFilter(queryset=Vendor.objects.filter(status='active'))
    src = django_filters.ModelChoiceFilter(queryset=Place.objects.all(), label='Source Place')
    dst = django_filters.ModelChoiceFilter(queryset=Place.objects.all(), label='Destination Place')
    min_quantity = django_filters.NumberFilter(method='filter_by_quantity', label='Min Quantity')
    unit = django_filters.ModelChoiceFilter(queryset=Unit.objects.all(), label='Unit')
    type = django_filters.ChoiceFilter(choices=PRODUCT_TYPE_CHOICES, label='Product Type')

    class Meta:
        model = Product
        fields = ['category', 'vendor', 'price_min', 'price_max', 'src', 'dst', 'min_quantity', 'unit', 'type']

    def filter_by_quantity(self, queryset, name, value):
        unit = self.data.get('unit')
        if unit:
            queryset = queryset.filter(quantity__gte=value, unit_id=unit)
        return queryset
