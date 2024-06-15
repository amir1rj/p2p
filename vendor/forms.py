from django import forms
from .models import Vendor, VendorImage


class VendorApplicationForm(forms.ModelForm):
    initial_image = forms.ImageField(required=True, label='Initial Image')

    class Meta:
        model = Vendor
        fields = ['description', 'initial_image']


class VendorImageForm(forms.ModelForm):
    class Meta:
        model = VendorImage
        fields = ['image']
