from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from order.models import Order, Freeze_money
from p2p.settings import SITE_PROFIT_PERCENT_VENDOR
from .models import Vendor, VendorImage
from .forms import VendorApplicationForm, VendorImageForm


class VendorApplicationView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorApplicationForm
    template_name = 'vendor/apply.html'
    success_url = "/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        VendorImage.objects.create(vendor=form.instance, image=form.cleaned_data['initial_image'])
        return response


class AddVendorImageView(LoginRequiredMixin, FormView):
    form_class = VendorImageForm
    template_name = 'vendor/add_image.html'
    success_url = '/'

    # success_url = reverse_lazy('vendor:image_added_success')

    def form_valid(self, form):
        vendor = get_object_or_404(Vendor, user=self.request.user)
        VendorImage.objects.create(vendor=vendor, image=form.cleaned_data['image'])
        return super().form_valid(form)


class ConfirmOrderView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if request.user != order.product.vendor.user:
            messages.error(request, "You are not authorized to confirm this order.")
            return redirect("orders:detail", order_id=order_id)
        return render(request, "vendor/confirm_order.html", {"order": order})

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if request.user != order.product.vendor.user:
            messages.error(request, "You are not authorized to confirm this order.")
            return redirect("orders:detail", order_id=order_id)

        action = request.POST.get("action")
        finalize_day = request.POST.get("finalize_day")
        if action == "approve":
            if not finalize_day or not finalize_day.isdigit() or int(finalize_day) < 0:
                messages.error(request, "Please provide a valid finalization date.")
                return redirect("orders:confirm_order", order_id=order_id)
            order.status = "approved"
            order.is_paid = True
            order.finalize_day = int(finalize_day)

            # Deduct balance from user
            order.user.balance -= order.total_price
            order.user.save()

            # Add balance to vendor

            real_price = order.quantity * order.product.price
            Freeze_money.objects.create(order=order,value=real_price - (real_price / SITE_PROFIT_PERCENT_VENDOR))
            # order.product.vendor.user.balance += real_price - (real_price / 10)
            # order.product.vendor.user.save()

            # Decrease the product quantity
            order.product.quantity -= order.quantity
            order.product.save()

            messages.success(request, "Order approved successfully.")
        elif action == "reject":
            order.status = "rejected"
            messages.success(request, "Order rejected successfully.")

        order.save()
        return redirect("orders:detail", order_id=order.id)


class VendorOrdersListView(LoginRequiredMixin, View):
    def get(self, request):
        vendor = get_object_or_404(Vendor, user=request.user)
        orders = Order.objects.filter(product__vendor=vendor, status="confirmed")
        return render(request, "vendor/orders_list.html", {"orders": orders})
