from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django_filters.views import FilterView

from product.filters import ProductFilter
from product.forms import ProductForm, InformationFormSet, ProductUpdateForm, ShippingOptionsFormSet
from product.models import Product, Image, ProductChangeRequest


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_form.html'
    success_url = '/'

    def dispatch(self, *args, **kwargs):
        if not hasattr(self.request.user, 'vendor') or self.request.user.vendor.status != 'active':
            return redirect('not_authorized')
        return super().dispatch(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['information_formset'] = InformationFormSet(self.request.POST)
            context['shipping_options_formset'] = ShippingOptionsFormSet(self.request.POST)
        else:
            context['information_formset'] = InformationFormSet()
            context['shipping_options_formset'] = ShippingOptionsFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        information_formset = context['information_formset']
        shipping_options_formset = context['shipping_options_formset']
        if information_formset.is_valid() and shipping_options_formset.is_valid():
            form.instance.vendor = self.request.user.vendor
            response = super().form_valid(form)

            # Save the initial image
            initial_image = form.cleaned_data.get('initial_image')
            if initial_image:
                Image.objects.create(product=self.object, image=initial_image)

            # Save additional images
            images = self.request.FILES.getlist('images')
            for image in images:
                Image.objects.create(product=self.object, image=image)

            # Save the information formset
            information_formset.instance = self.object
            information_formset.save()

            # Save the shipping options formset
            shipping_options_formset.instance = self.object
            shipping_options_formset.save()

            # Call the custom method to add parent categories
            self.object.add_parent_categories()

            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))


class VendorProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'vendor/vendor_products.html'

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user.vendor)


class ProductListView(FilterView, ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    filterset_class = ProductFilter
    paginate_by = 10  # Optional pagination

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='active')  # Only show active products
        sort = self.request.GET.get('sort', 'newest')

        if sort == 'newest':
            queryset = queryset.order_by('-create_datetime')
        elif sort == 'oldest':
            queryset = queryset.order_by('create_datetime')
        elif sort == 'random':
            queryset = queryset.order_by('?')
        elif sort == 'quantity_asc':
            queryset = queryset.order_by('quantity')
        elif sort == 'quantity_desc':
            queryset = queryset.order_by('-quantity')
        return queryset


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductChangeRequest
    form_class = ProductUpdateForm
    template_name = 'product/product_form.html'
    success_url = '/'

    def dispatch(self, *args, **kwargs):
        if not hasattr(self.request.user, 'vendor') or self.request.user.vendor.status != 'active':
            return redirect('not_authorized')
        return super().dispatch(self.request, *args, **kwargs)

    def get_object(self, queryset=None):
        product_slug = self.kwargs['slug']
        product = get_object_or_404(Product, slug=product_slug)
        change_request = ProductChangeRequest.objects.filter(product=product, vendor=self.request.user.vendor,
                                                             request_status='pending').last()
        if change_request:
            return change_request
        return ProductChangeRequest(
            product=product,
            vendor=self.request.user.vendor,
            title=product.title,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
        )

    def form_valid(self, form):
        change_request = form.save(commit=False)
        change_request.product = self.get_object().product
        change_request.vendor = self.request.user.vendor

        if change_request.title != change_request.product.title or \
                change_request.description != change_request.product.description or \
                change_request.price != change_request.product.price or \
                change_request.quantity != change_request.product.quantity or \
                list(change_request.categories.all()) != list(change_request.product.category.all()):
            change_request.save()
            form.save_m2m()

            change_request.categories.set(form.cleaned_data['categories'])
            change_request.save()
        return super().form_valid(form)


@staff_member_required
def review_change_requests(request):
    change_requests = ProductChangeRequest.objects.filter(is_approved=False)
    return render(request, 'product/review_change_requests.html', {'change_requests': change_requests})


@staff_member_required
def approve_change_request(request, pk):
    change_request = get_object_or_404(ProductChangeRequest, pk=pk)
    product = change_request.product
    product.title = change_request.title
    product.description = change_request.description
    product.price = change_request.price
    product.is_promoted = change_request.is_promoted
    product.quantity = change_request.quantity
    product.status = change_request.status
    product.save()

    change_request.is_approved = True
    change_request.save()

    return redirect('review_change_requests')


@staff_member_required
def reject_change_request(request, pk):
    change_request = get_object_or_404(ProductChangeRequest, pk=pk)
    change_request.delete()
    return redirect('review_change_requests')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
