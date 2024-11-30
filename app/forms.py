from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from app import models


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class SignupForm(forms.Form):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirmation = forms.CharField(widget=forms.PasswordInput, required=True)
    avatar = forms.ImageField(required=False)

    def clean(self):
        password = self.cleaned_data['password']
        password_confirmation = self.cleaned_data['password_confirmation']
        if password != password_confirmation:
            raise ValidationError("Passwords don't match")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email already exists')

    def save(self):
        avatar=self.cleaned_data['avatar']
        self.cleaned_data.pop('avatar')
        self.cleaned_data.pop('password_confirmation')
        user = User.objects.create_user(**self.cleaned_data)
        models.Profile.objects.create(user=user, avatar=avatar)
        return user


class SettingsForm(forms.Form):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists() and username != self.user.username:
            raise ValidationError('This username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists() and email != self.user.email:
            raise ValidationError('This email already exists')
        return email

    def save(self):
        self.user.profile.username = self.cleaned_data['username']
        self.user.profile.email = self.cleaned_data['email']
        self.user.profile.avatar = self.cleaned_data['avatar']
        self.user.profile.save()
        return self.user







