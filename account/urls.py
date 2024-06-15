from django.urls import path
from .views import user_logout, UserRegisterView, UserLoginView, PinCodeChangeView, \
    RecoveryPasswordStepOneView, RecoveryPasswordStepTwoView, Confirm_pin_code,ChangePasswordView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('change-pin-code/', PinCodeChangeView.as_view(), name='change_pin_code'),
    path("recovery-password/step-one/", RecoveryPasswordStepOneView.as_view(), name="recovery_password_step_one"),
    path("recovery-password/step-two/", RecoveryPasswordStepTwoView.as_view(), name="recovery_password_step_two"),
    path("pin-code-confirm/", Confirm_pin_code.as_view(), name="pin_code_confirmation"),
    path("change-password/",ChangePasswordView.as_view(), name="change_password")
]
