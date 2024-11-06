from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    profile = models.OneToOneField(User, null=True, on_delete=models.PROTECT, default="")
    avatar = models.ImageField(null=True, upload_to='avatar/', blank=True, default='profile.jpg')

    def __str__(self):
        return self.profile


class Question(models.Model):
    title = models.CharField(max_length=30, blank=False)
    content = models.CharField(max_length=300, blank=False)
    profile = models.ForeignKey('Profile', on_delete=models.PROTECT, blank=True, null=True, default="")
    tags = models.ManyToManyField('Tag', blank=True)
    likes = models.IntegerField(default=0)
    date = models.DateField(blank=False, null=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(blank=False, max_length=10)

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, blank=False, default="")
    content = models.TextField(blank=False)
    profile = models.ForeignKey('Profile', on_delete=models.PROTECT, blank=True, null=True, default="")
    rating = models.IntegerField(default=0)
    date = models.DateField(blank=False, null=True)


class QuestionLike(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    like = models.BooleanField()

    class Meta:
        unique_together = ('question', 'user')

    def __str__(self):
        return self.profile


class AnswerLike(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    like = models.BooleanField()

    class Meta:
        unique_together = ('answer', 'user')

    def __str__(self):
        return self.profile
