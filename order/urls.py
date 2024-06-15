# urls.py
from django.urls import path
from .views import CreateOrderView, OrderDetailView, CancelOrderView

app_name = 'orders'
urlpatterns = [
    path("create/<int:product_id>/", CreateOrderView.as_view(), name="create"),
    path("detail/<int:order_id>/", OrderDetailView.as_view(), name="detail"),
    path("cancel/<int:order_id>/", CancelOrderView.as_view(), name="cancel_order"),
]
