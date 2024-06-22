from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.views.generic import ListView, DetailView

from order.forms import ShippingDetailsForm, MessageForm
from order.models import Order, Chat
from p2p.settings import SITE_PROFIT_PERCENT_USER
from product.models import Product, Shipping_options, Coupon


class CreateOrderView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        shipping_options = product.shipping_options.all()
        form = ShippingDetailsForm()
        return render(request, "order/create_order.html", {
            "product": product,
            "shipping_options": shipping_options, "form": form
        })

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get("quantity"))
        shipping_option_id = request.POST.get("shipping_option")
        shipping_option = get_object_or_404(Shipping_options, id=shipping_option_id)

        if quantity > product.quantity:
            messages.error(request, "Not enough stock available.")
            return redirect("product_detail", product_id=product_id)
        form = ShippingDetailsForm(request.POST)
        if form.is_valid():
            shipping_details = form.save(commit=False)
            shipping_details.user = request.user
            shipping_details.save()

            order = Order.objects.create(
                user=request.user,
                product=product,
                shipping_option=shipping_option,
                quantity=quantity,
                status="pending",
                shipping_details=shipping_details  # Associate shipping details with the order
            )

            messages.success(request, "Order created successfully.")
            return redirect("orders:detail", order_id=order.id)
        else:
            # If form is not valid, re-render the form with errors
            shipping_options = product.shipping_options.all()
            return render(request, "order/create_order.html", {
                "product": product,
                "shipping_options": shipping_options,
                "form": form
            })


# class CreateOrderView(LoginRequiredMixin, View):
#     def get(self, request, product_id):
#         product = get_object_or_404(Product, id=product_id)
#         shipping_options = product.shipping_options.all()
#         return render(request, "order/create_order.html", {"product": product, "shipping_options": shipping_options})
#
#     def post(self, request, product_id):
#         product = get_object_or_404(Product, id=product_id)
#         quantity = int(request.POST.get("quantity"))
#         shipping_option_id = request.POST.get("shipping_option")
#         shipping_option = get_object_or_404(Shipping_options, id=shipping_option_id)
#
#         if quantity > product.quantity:
#             messages.error(request, "Not enough stock available.")
#             return redirect("product_detail", product_id=product_id)
#
#         order = Order.objects.create(
#             user=request.user,
#             product=product,
#             shipping_option=shipping_option,
#             quantity=quantity,
#             status="pending"
#         )
#
#         messages.success(request, "Order created successfully.")
#         return redirect("orders:detail", order_id=order.id)


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        product_price = order.product.price * order.quantity
        return render(request, "order/order_detail.html",
                      {"order": order, "shipping_price": order.shipping_option.price,
                       "site_profit": product_price / SITE_PROFIT_PERCENT_USER})

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

            order.status = "confirmed"
            order.save()

        elif action == "completed":
            order.status = "completed"
            order.product.vendor.user.balance += order.suspend_money.value
            order.product.vendor.user.save()
            order.save()
            messages.success(request, "Order confirmed successfully.")

        elif action == "apply_coupon":
            coupon_code = request.POST.get("coupon_code")
            coupon = Coupon.objects.filter(code=coupon_code).first()
            if coupon:
                is_valid = coupon.is_valid(user=request.user.id,order=order)
                if is_valid["bool"]:
                    discount = Decimal(coupon.amount)
                    if coupon.type == 'percent':
                        discount = (order.total_price * discount) / 100
                    discount = min(discount, Decimal(coupon.max_value))
                    order.total_price -= discount
                    order.total_price = order.total_price.quantize(Decimal('0.01'))

                    coupon.use_coupon(request.user.id)
                    order.save(recalculate_total=False)
                    messages.success(request, "Coupon applied successfully.")
                else:
                    messages.error(request, is_valid["msg"])
            else:
                messages.error(request, "Invalid coupon code.")

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


class DelayOrderView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if request.user != order.product.vendor.user and request.user != order.user:
            messages.error(request, "You are not authorized to delay this order.")
            return redirect("orders:detail", order_id=order_id)
        return render(request, "order/delay_order.html", {"order": order})

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if request.user != order.product.vendor.user and request.user != order.user:
            messages.error(request, "You are not authorized to delay this order.")
            return redirect("orders:detail", order_id=order_id)

        delay_days = request.POST.get("delay_days")
        if not delay_days or not delay_days.isdigit() or int(delay_days) < 0:
            messages.error(request, "Please provide a valid delay period.")
            return redirect("orders:delay_order", order_id=order_id)

        order.finalize_day += int(delay_days)
        order.status = "delayed"
        order.save()

        messages.success(request, "Order delayed successfully.")
        return redirect("orders:detail", order_id=order.id)


class UserChatsView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'order/user_chats.html'
    context_object_name = 'chats'

    def get_queryset(self):
        return Chat.objects.filter(
            Q(user=self.request.user) | Q(vendor__user=self.request.user)
        )


class ChatDetailView(LoginRequiredMixin, View):
    template_name = 'order/chat_detail.html'
    context_object_name = 'chat'

    def get_object(self):
        chat = get_object_or_404(
            Chat,
            Q(pk=self.kwargs['chat_id']) &
            (Q(user=self.request.user) | Q(vendor__user=self.request.user))
        )
        return chat

    def get(self, request, *args, **kwargs):
        chat = self.get_object()
        messages = chat.messages.all()
        form = MessageForm()
        message_text = "\n".join(
            [f"{msg.author}: {msg.content} ({msg.create_datetime})" for msg in messages])

        context = {
            'chat': chat,
            'messages': messages,
            'form': form,
            'message_text': message_text,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        chat = self.get_object()
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.chat = chat
            message.save()
            return redirect('orders:chat_detail', chat_id=chat.id)

        messages = chat.messages.all()
        message_text = "\n".join(
            [f"{msg.author}: {msg.content} ({msg.timestamp})" for msg in messages])

        context = {
            'chat': chat,
            'messages': messages,
            'form': form,
            'message_text': message_text,
        }
        return render(request, self.template_name, context)
