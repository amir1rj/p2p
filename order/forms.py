from django import forms
from .models import Shipping_details, Message


class ShippingDetailsForm(forms.ModelForm):
    class Meta:
        model = Shipping_details
        fields = ['type', 'address', 'city', 'state', 'country', 'zipcode', 'phone', 'email', 'description',
                  'auth_info', 'account_address']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
