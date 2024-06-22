from django import forms

from order.models import Order
from .models import Ticket, Message


class TicketForm(forms.ModelForm):
    order = forms.ModelChoiceField(queryset=Order.objects.none())

    class Meta:
        model = Ticket
        fields = ['subject', 'order']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['order'].queryset = Order.objects.filter(user=user)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
