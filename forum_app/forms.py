from django import forms
from django.contrib.auth.models import User
from .models import Question, Answer

import re
from django.core.exceptions import ValidationError

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a strong password'}),
        help_text="At least 8 characters, with uppercase, lowercase, number, and special character."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Password match check
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        # Password strength check
        if password:
            if len(password) < 8:
                self.add_error('password', "Password must be at least 8 characters long")
            if not re.search(r'[A-Z]', password):
                self.add_error('password', "Password must contain at least one uppercase letter")
            if not re.search(r'[a-z]', password):
                self.add_error('password', "Password must contain at least one lowercase letter")
            if not re.search(r'[0-9]', password):
                self.add_error('password', "Password must contain at least one number")
            if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
                self.add_error('password', "Password must contain at least one special character")


class LoginForm(forms.Form):
    username = forms.CharField(label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput)

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(required=False, help_text='Comma separated tags')

    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']
