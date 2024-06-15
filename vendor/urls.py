from django.urls import path

from product.views import VendorProductListView
from .views import VendorApplicationView, AddVendorImageView, VendorOrdersListView, ConfirmOrderView

app_name = 'vendor'
urlpatterns = [
    path('apply/', VendorApplicationView.as_view(), name='apply'),
    path('products/', VendorProductListView.as_view(), name='products'),
    path('add_image/', AddVendorImageView.as_view(), name='add_image'),
    path("orders/", VendorOrdersListView.as_view(), name="orders_list"),
    path("confirm/<int:order_id>/", ConfirmOrderView.as_view(), name="confirm_order"),

]
