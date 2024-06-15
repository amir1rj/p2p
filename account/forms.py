import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model

from account.utils import generate_math_captcha

User = get_user_model()

from django.contrib.auth.forms import AuthenticationForm

SESSION_DURATIONS = [
    (30 * 60, "30 minutes"),
    (2 * 60 * 60, "2 hours"),
    (3 * 60 * 60, "3 hours"),
    (6 * 60 * 60, "6 hours"),
]


class UserRegisterForm(UserCreationForm):
    display_name = forms.CharField(max_length=255, required=True, label='Display Name',
                                   widget=forms.TextInput(attrs={"class": "form-control"}))
    captcha = forms.CharField(max_length=255, required=True, label='Captcha',
                              widget=forms.TextInput(attrs={"class": "form-control"}))
    captcha_question = forms.CharField(widget=forms.HiddenInput(), required=False)
    PGP_key = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 40, "class": "form-control"}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}), )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}))
    pin_code = forms.CharField(widget=forms.NumberInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ['username', 'pin_code', 'PGP_key', 'password1', 'password2', 'display_name', 'captcha']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        question, answer = generate_math_captcha()
        self.fields['captcha'].label = question
        self.fields['captcha_question'].initial = answer

    def clean_pin_code(self):
        pin_code = self.cleaned_data.get('pin_code')
        if not str(pin_code).isdigit() or len(str(pin_code)) != 6:
            raise forms.ValidationError("PIN code must be exactly 6 digits long.")
        return pin_code

    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name')
        # Your custom validation logic for display_name
        if any(char.isspace() for char in display_name):
            raise forms.ValidationError("Display name cannot contain spaces.")
        return display_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Your custom validation logic for username
        if not re.match(r'^[A-Za-z0-9._]+$', username):
            raise forms.ValidationError(
                'Username can only contain letters, digits, dots, and underscores.'
            )

        return username

    def clean_new_password(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password1):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")

        return password1


class UserLoginForm(AuthenticationForm):
    session_duration = forms.ChoiceField(
        choices=SESSION_DURATIONS, label="Session Duration",
        widget=forms.Select(attrs={"class": "form-select form-control"})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class PinCodeChangeForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}))
    new_pin_code = forms.CharField(widget=forms.NumberInput(attrs={"class": "form-control"}))


class RecoveryPasswordStepOneForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}), )
    captcha = forms.CharField(max_length=255, required=True, label='Captcha',
                              widget=forms.TextInput(attrs={"class": "form-control"}))
    captcha_question = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        question, answer = generate_math_captcha()
        self.fields['captcha'].label = question
        self.fields['captcha_question'].initial = answer


class RecoveryPasswordStepTwoForm(forms.Form):
    recovery_password_or_pgp = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 40, "class": "form-control"}))
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if len(new_password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', new_password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[A-Z]', new_password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', new_password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")

        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError('The new password and confirm password fields do not match.')


class Confirm_pin_code(forms.Form):
    pin_code = forms.CharField(widget=forms.NumberInput(attrs={"class": "form-control"}))


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if len(new_password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', new_password1):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[A-Z]', new_password1):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', new_password1):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")

        return new_password1

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', "The two password fields must match.")

        return cleaned_data
