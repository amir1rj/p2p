from django import forms
from .models import Product, Information, Category, ProductChangeRequest, Shipping_options
from django.forms import inlineformset_factory


class ProductForm(forms.ModelForm):
    initial_image = forms.ImageField(required=True, label='Initial Image')
    shipping_options = forms.ModelMultipleChoiceField(
        queryset=Shipping_options.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'price', 'status', 'quantity', 'unit', 'src', 'dst', 'type', 'initial_image', 'shipping_options']

    def __init__(self, *args, **kwargs):
        vendor = kwargs.pop('vendor', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        if vendor:
            self.fields['shipping_options'].queryset = Shipping_options.objects.filter(vendor=vendor)


class ProductUpdateForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = ProductChangeRequest
        fields = ['title', 'categories', 'description', 'price', 'quantity', ]


class InformationForm(forms.ModelForm):
    class Meta:
        model = Information
        fields = ['text']


class ShippingOptionsForm(forms.ModelForm):
    class Meta:
        model = Shipping_options
        fields = ['text',"price"]


InformationFormSet = inlineformset_factory(Product, Information, form=InformationForm, extra=3, can_delete=True)
