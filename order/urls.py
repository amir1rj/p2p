# urls.py
from django.urls import path
from .views import CreateOrderView, OrderDetailView, CancelOrderView, DelayOrderView, UserChatsView, ChatDetailView

app_name = 'orders'
urlpatterns = [
    path('chats/', UserChatsView.as_view(), name='user_chats'),
    path('chat/<int:chat_id>/', ChatDetailView.as_view(), name='chat_detail'),
    path("create/<int:product_id>/", CreateOrderView.as_view(), name="create"),
    path("detail/<int:order_id>/", OrderDetailView.as_view(), name="detail"),
    path("cancel/<int:order_id>/", CancelOrderView.as_view(), name="cancel_order"),
    path("delay/<int:order_id>/", DelayOrderView.as_view(), name="delay"),
]
