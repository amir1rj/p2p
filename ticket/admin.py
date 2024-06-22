from django.contrib import admin

from ticket.models import Ticket, Message


# Register your models here.
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["__str__"]


@admin.register(Message)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ["__str__"]


