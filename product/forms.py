from django import forms
from .models import Product, Information, Category, ProductChangeRequest
from django.forms import inlineformset_factory


class ProductForm(forms.ModelForm):
    initial_image = forms.ImageField(required=True, label='Initial Image')

    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'price', 'status', 'quantity', 'unit', 'src', 'dst', 'type',
                  'initial_image']


class ProductUpdateForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = ProductChangeRequest
        fields = ['title', 'categories', 'description', 'price', 'quantity', ]


class InformationForm(forms.ModelForm):
    class Meta:
        model = Information
        fields = ['text']


InformationFormSet = inlineformset_factory(Product, Information, form=InformationForm, extra=3, can_delete=True)
