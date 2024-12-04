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
        if len(password) < 8:
            raise ValidationError('Password is too short')
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
        return email

    def save(self):
        avatar = self.cleaned_data['avatar']
        user = User.objects.create_user(username=self.cleaned_data['username'],
                                        email=self.cleaned_data['email'],
                                        password=self.cleaned_data['password'])
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
        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data.get('avatar')
            profile.save()

        return user


class AskForm(forms.ModelForm):
    tags = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                        'placeholder': 'Example: maths, physics, chemistry',
                                                                        'rows': '1'}))
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                         'placeholder': 'Enter your title',
                                                                         'rows': '10'}))
    content = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control',
                                                                          'placeholder': 'Enter your content',
                                                                          'rows': '1'}))

    class Meta:
        model = models.Question
        fields = ('title', 'content', 'tags')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tags = tags.split(', ')
        if len(tags) < 0:
            raise ValidationError('Tags cannot be empty')
        if len(tags) > 8:
            raise ValidationError('Too much tags, 8 is maximum')
        return tags

    def clean_title(self):
        title = self.cleaned_data['title']
        if models.Question.objects.filter(title=title).exists():
            raise ValidationError('This title already exists')
        if len(title) < 1:
            raise ValidationError('Title cannot be empty')
        return title

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 1:
            raise ValidationError('Content cannot be empty')
        return content

    def save(self):
        profile = models.Profile.objects.get(user=self.user)
        question = models.Question(author=profile, title=self.cleaned_data['title'],
                                   content=self.cleaned_data['content'])
        question.save()

        tags = self.cleaned_data.get('tags')

        tags_set = set()
        for i in tags:
            tags_set.add(models.Tag.objects.get_or_create(name=i.strip())[0])

        question.tags.set(list(tags_set))
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ('content',)

    def __init__(self, user, question_id, *args, **kwargs):
        self.user = user
        self.question_id = question_id
        super().__init__(*args, **kwargs)

    def clean_content(self):
        if len(self.cleaned_data['content']) < 1:
            raise ValidationError('Content cannot be empty')
        return self.cleaned_data['content']

    def save(self):
        question = models.Question.objects.get(id=self.question_id)
        question.amount_of_answers += 1
        question.save()
        author = models.Profile.objects.get(user=self.user)
        answer = models.Answer(author=author, question=question, content=self.cleaned_data['content'])
        answer.save()
        return answer