from datetime import timedelta

from django.db import models
from django.utils import timezone

from core.models import BaseModel
from p2p import settings
from p2p.settings import DAY_TO_CLOSE_TICKET
from order.models import Order

TICKET_STATUS = (
    ("pending", "Pending"),
    ("answered", "Answered"),
    ("closed", "Closed"),
)


class Ticket(BaseModel):
    subject = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=TICKET_STATUS, default="pending")
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="tickets", null=True, blank=True)

    def __str__(self):
        return f"{self.subject}: {self.user} "

    def is_closed(self):
        final_date = self.create_datetime + timedelta(days=DAY_TO_CLOSE_TICKET)
        if self.status == "closed":
            return True
        if self.status == "answered":
            return timezone.now() >= final_date


class Message(BaseModel):
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ticket_messages')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")

    def last_messages(self):
        return Message.objects.order_by('-create_datetime').filter(ticket__id=self.ticket.id)

    def __str__(self):
        return f" {self.content[:30]} -- {self.ticket}"
