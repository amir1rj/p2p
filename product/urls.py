from django.urls import path
from django.views.generic import TemplateView

from .views import ProductCreateView, ProductListView, ProductUpdateView, review_change_requests, \
    approve_change_request, reject_change_request, ProductDetailView

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='create_product'),
    path('update/<slug:slug>/', ProductUpdateView.as_view(), name='product_update'),
    path('change-requests/', review_change_requests, name='review_change_requests'),
    path('change-requests/<int:pk>/approve/', approve_change_request, name='approve_change_request'),
    path('change-requests/<int:pk>/reject/', reject_change_request, name='reject_change_request'),
    path('not-authorized/', TemplateView.as_view(template_name='product/not_authorized.html'), name='not_authorized'),
    path('list/', ProductListView.as_view(), name='product_list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]
