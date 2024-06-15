from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import UserRegisterForm, UserLoginForm, PinCodeChangeForm, \
    RecoveryPasswordStepOneForm, RecoveryPasswordStepTwoForm, Confirm_pin_code, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Profile, TempPassword

User = get_user_model()


class UserRegisterView(FormView):
    template_name = 'account/register.html'
    form_class = UserRegisterForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        captcha_input = form.cleaned_data['captcha']
        captcha_answer = form.cleaned_data['captcha_question']

        # if captcha_input != captcha_answer:
        #     form.add_error('captcha', 'Incorrect answer to the math question')
        #     return self.form_invalid(form)

        user = form.save()
        display_name = form.cleaned_data['display_name']
        Profile.objects.create(user=user, profile_name=display_name)
        login(self.request, user)
        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = 'account/login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        session_duration = int(form.cleaned_data.get('session_duration'))
        self.request.session.set_expiry(session_duration)
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        print("Next URL: ", next_url)
        if next_url:
            return next_url
        return '/'


class PinCodeChangeView(LoginRequiredMixin, FormView):
    template_name = 'account/change_pin_code.html'
    form_class = PinCodeChangeForm
    success_url = '/'

    def form_valid(self, form):
        password = form.cleaned_data['password']
        new_pin_code = form.cleaned_data['new_pin_code']
        user = self.request.user

        if not user.check_password(password):
            form.add_error('password', 'Invalid password.')
            return self.form_invalid(form)

        user.pin_code = new_pin_code
        user.save()
        messages.success(self.request, 'Your pin code has been updated!')
        return super().form_valid(form)


def user_logout(request):
    logout(request)
    return redirect("/")


# class RecoveryPasswordStepOneView(FormView):
#     template_name = 'account/recovery_password_step_one.html'
#     form_class = RecoveryPasswordStepOneForm
#     success_url = reverse_lazy('recovery_password_step_two')
#
#     def form_valid(self, form):
#         username = form.cleaned_data['username']
#         captcha_input = form.cleaned_data['captcha']
#         captcha_answer = form.cleaned_data['captcha_question']
#
#         # if captcha_input != captcha_answer:
#         #     form.add_error('captcha', 'Incorrect answer to the math question')
#         #     return self.form_invalid(form)
#
#         if self.request.user.username != username:
#             form.add_error('username', 'Username is incorrect.')
#             return self.form_invalid(form)
#         return super().form_valid(form)


class RecoveryPasswordStepOneView(FormView):
    template_name = 'account/recovery_password_step_one.html'
    form_class = RecoveryPasswordStepOneForm
    success_url = reverse_lazy('recovery_password_step_two')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
            self.request.session['recovery_user_id'] = user.pk  # Store user ID in session
            return super().form_valid(form)
        except User.DoesNotExist:
            form.add_error("username", 'username does not exist')
            return self.form_invalid(form)


class RecoveryPasswordStepTwoView(FormView):
    template_name = 'account/recovery_password_step_two.html'
    form_class = RecoveryPasswordStepTwoForm
    success_url = reverse_lazy('pin_code_confirmation')

    def dispatch(self, request, *args, **kwargs):
        # Ensure user ID exists in session, redirect to step one if not
        if 'recovery_user_id' not in self.request.session:
            return redirect('recovery_password_step_one')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user_id = self.request.session.get('recovery_user_id')
        recovery_password_or_pgp = form.cleaned_data['recovery_password_or_pgp']
        new_password = form.cleaned_data['new_password']
        user = User.objects.get(pk=user_id)
        if user.recovery_password == recovery_password_or_pgp or user.PGP_key == recovery_password_or_pgp:
            self.request.session['recovery_user_id'] = user_id  # Update user ID in session
            self.request.session['recovery_new_password'] = new_password  # Store new password in session
            return super().form_valid(form)
        else:
            form.add_error("recovery_password_or_pgp", 'Invalid recovery password or PGP key.')
            return self.form_invalid(form)


class Confirm_pin_code(FormView):
    template_name = 'account/pin_code_confirmation.html'
    form_class = Confirm_pin_code
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if 'recovery_user_id' not in self.request.session or 'recovery_new_password' not in self.request.session:
            return redirect('recovery_password_step_one')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
        else:
            user_id = self.request.session.get('recovery_user_id')
        user = User.objects.get(pk=user_id)
        new_password = TempPassword.objects.filter(user=user).last().temp_password
        pin_code = form.cleaned_data['pin_code']
        try:
            user = User.objects.get(pk=user_id)
            if str(user.pin_code) == str(pin_code):

                user.set_password(new_password)
                user.save()
                messages.success(self.request, 'Your password has been updated!')
                if not self.request.user.is_authenticated:
                    del self.request.session['recovery_user_id']  # Clear session data

                return super().form_valid(form)
            else:
                form.add_error("pin_code", 'Invalid pin_code')
                return self.form_invalid(form)
        except User.DoesNotExist:
            messages.error(self.request, 'User not found.')
            return self.form_invalid(form)


# class RecoveryPasswordStepTwoView(FormView):
#     template_name = 'account/recovery_password_step_two.html'
#     form_class = RecoveryPasswordStepTwoForm
#     success_url = reverse_lazy('recovery_password_step_three')
#
#     def form_valid(self, form):
#         username = self.request.user.username
#         recovery_password_or_pgp = form.cleaned_data['recovery_password_or_pgp']
#         new_password = form.cleaned_data['new_password']
#
#         user = User.objects.get(username=username)
#         if user.recovery_password == recovery_password_or_pgp or user.PGP_key == recovery_password_or_pgp:
#             temp_password = \
#                 TempPassword.objects.get_or_create(user=user, temp_password=new_password, created_at=timezone.now())
#
#             return super().form_valid(form)
#         else:
#             form.add_error("recovery_password_or_pgp", 'Invalid recovery password or PGP key.')
#             return self.form_invalid(form)


# class RecoveryPasswordStepThreeView(FormView):
#     template_name = 'account/pin_code_confirmation.html'
#     form_class = RecoveryPasswordStepThreeForm
#     success_url = reverse_lazy('login')
#
#     def form_valid(self, form):
#         username = self.request.user.username
#         temp_password_id = self.request.user.tmp_passwords.first().id
#         pin_code = form.cleaned_data['pin_code']
#
#         try:
#             user = User.objects.get(username=username)
#             temp_password = TempPassword.objects.get(id=temp_password_id)
#             if str(user.pin_code) == str(pin_code) and temp_password.is_valid():
#                 user.set_password(temp_password.temp_password)
#                 user.save()
#                 messages.success(self.request, 'Your password has been updated!')
#                 temp_password.delete()
#                 return super().form_valid(form)
#             else:
#                 form.add_error("pin_code", 'Invalid pin code.')
#                 return self.form_invalid(form)
#         except User.DoesNotExist:
#             messages.error(self.request, 'Invalid username.')
#             return self.form_invalid(form)
#         except TempPassword.DoesNotExist:
#             messages.error(self.request, 'Temporary password not found.')
#             return self.form_invalid(form)

class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'account/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('pin_code_confirmation')

    def form_valid(self, form):
        user = self.request.user
        old_password = form.cleaned_data['old_password']
        new_password = form.cleaned_data['new_password1']
        confirm_new_password = form.cleaned_data['new_password2']

        if not user.check_password(old_password):
            form.add_error('old_password', 'Incorrect old password.')
            return self.form_invalid(form)

        if new_password != confirm_new_password:
            form.add_error('new_password2', 'New passwords do not match.')
            return self.form_invalid(form)

        temp_password = TempPassword.objects.get_or_create(user=user, temp_password=new_password,
                                                           created_at=timezone.now())
        # print(temp_password.)
        return super().form_valid(form)
