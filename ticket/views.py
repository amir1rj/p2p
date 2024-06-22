from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View


from ticket.forms import TicketForm, MessageForm
from ticket.models import Ticket


# Create your views here.
class TicketDetailView(LoginRequiredMixin, View):
    template_name = 'ticket/ticket_detail.html'
    context_object_name = 'ticket'

    def get_object(self):
        ticket = get_object_or_404(
            Ticket,
            Q(pk=self.kwargs['ticket_id']) &
            Q(user=self.request.user)
        )
        return ticket

    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        messages = ticket.messages.all()
        form = MessageForm()
        message_text = "\n".join(
            [f"{msg.author}: {msg.content} ({msg.create_datetime})" for msg in messages])

        context = {
            'ticket': ticket,
            'messages': messages,
            'form': form,
            'message_text': message_text,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.ticket = ticket
            message.save()
            return redirect('tickets:ticket_detail', ticket_id=ticket.id)

        messages = ticket.messages.all()
        message_text = "\n".join(
            [f"{msg.author}: {msg.content} ({msg.create_datetime})" for msg in messages])

        context = {
            'ticket': ticket,
            'messages': messages,
            'form': form,
            'message_text': message_text,
        }
        return render(request, self.template_name, context)


class UserTicketsView(LoginRequiredMixin, View):
    template_name = 'ticket/user_tickets.html'

    def get(self, request):
        tickets = Ticket.objects.filter(user=request.user)
        return render(request, self.template_name, {'tickets': tickets})


class CreateTicketView(LoginRequiredMixin, View):
    def get(self, request):
        ticket_form = TicketForm(user=request.user)  # Pass user to the form
        message_form = MessageForm()
        return render(request, 'ticket/create_ticket.html', {'ticket_form': ticket_form, 'message_form': message_form})

    def post(self, request):
        ticket_form = TicketForm(request.POST, user=request.user)  # Pass user to the form
        message_form = MessageForm(request.POST)
        if ticket_form.is_valid() and message_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            message = message_form.save(commit=False)
            message.author = request.user
            message.ticket = ticket
            message.save()

            return redirect('tickets:ticket_success')
        return render(request, 'ticket/create_ticket.html', {'ticket_form': ticket_form, 'message_form': message_form})

class TicketSuccessView(View):
    def get(self, request):
        return render(request, 'ticket/ticket_success.html')
