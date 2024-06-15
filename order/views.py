from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages

from order.models import Order
from p2p.settings import SITE_PROFIT_PERCENT_USER
from product.models import Product


class CreateOrderView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        return render(request, "order/create_order.html", {"product": product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get("quantity"))
        if quantity > product.quantity:
            messages.error(request, "Not enough stock available.")
            return redirect("product_detail", product_id=product_id)

        # total_price = (quantity * product.price) + (
        #         (quantity * product.price) / SITE_PROFIT_PERCENT)

        order = Order.objects.create(
            user=request.user,
            product=product,
            # total_price=total_price,
            quantity=quantity,
            status="pending"
        )

        messages.success(request, "Order created successfully.")
        # return redirect("order_detail", order_id=order.id)
        return redirect("orders:detail", order_id=order.id)


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, "order/order_detail.html", {"order": order})

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if request.user != order.user:
            messages.error(request, "You are not authorized to update this order.")
            return redirect("orders:detail", order_id=order_id)
        action = request.POST.get("action")
        if action == "confirmed":
            if request.user.balance < order.total_price:
                messages.error(request, "Insufficient balance to confirm this order.")
                return redirect("orders:detail", order_id=order_id)
        elif action == "completed":
            order.status = "completed"
            order.product.vendor.user.balance += order.suspend_money.value
            order.product.vendor.user.save()
            order.save()
            messages.success(request, "Order confirmed successfully.")

        return redirect("orders:detail", order_id=order.id)


class CancelOrderView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if request.user != order.user:
            messages.error(request, "You are not authorized to cancel this order.")
            return redirect("orders:detail", order_id=order_id)

        if order.status in ['pending', 'confirmed']:
            order.status = "canceled"
            order.save()
            messages.success(request, "Order canceled successfully.")
        else:
            messages.error(request, "You cant cancel this order now.")

        return redirect("orders:detail", order_id=order.id)
