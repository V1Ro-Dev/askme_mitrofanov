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


class SettingsForm(forms.ModelForm):
    password_confirmation = forms.CharField(widget=forms.PasswordInput, required=True)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'password': forms.PasswordInput,
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')
        if len(password) < 8:
            raise ValidationError('Password is too short')
        if password and password != password_confirmation:
            raise ValidationError("Passwords don't match")
        return cleaned_data

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
        user = super().save()
        if self.cleaned_data.get('password') != '':
            user.set_password(self.cleaned_data['password'])
        user.username = self.cleaned_data.get('username')
        user.email = self.cleaned_data.get('email')
        user.save()

        profile = user.profile
        print(self.cleaned_data.get('avatar'))
        if self.cleaned_data.get('avatar'):
            print('Сохраняем')
            profile.avatar = self.cleaned_data.get('avatar')
            profile.save()

        return user







