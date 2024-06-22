

from django.urls import path
from .views import CreateTicketView, TicketSuccessView, UserTicketsView, TicketDetailView
app_name = 'tickets'
urlpatterns = [
    path('create/', CreateTicketView.as_view(), name='create_ticket'),
    path('success/', TicketSuccessView.as_view(), name='ticket_success'),
    path('list/', UserTicketsView.as_view(), name='user_tickets'),
    path('<int:ticket_id>/', TicketDetailView.as_view(), name='ticket_detail'),
]