from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from app.models import Question, Answer, Profile, AnswerLike, QuestionLike, Tag, User
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        print(datetime.now())
        ratio = options['ratio']

        tags_size = ratio
        likes_size = ratio * 200
        questions_size = ratio * 10
        profiles_size = ratio
        answers_size = ratio * 100

        profiles = [
            Profile(
                user=User.objects.create_user(
                    username=f'{fake.user_name()} {i}',
                    password=fake.password(),
                    email=fake.email()
                )
            ) for i in range(profiles_size)]

        Profile.objects.bulk_create(profiles)
        profiles = Profile.objects
        profiles_amount = profiles.count()

        tags = [Tag(name=fake.word()) for i in range(tags_size)]

        Tag.objects.bulk_create(tags)
        tags = Tag.objects
        tags_count = tags.count()

        questions = []

        for i in range(questions_size):
            q = Question(
                title=fake.sentence(nb_words=3),
                content=fake.text(max_nb_chars=512),
                likes=random.randint(0, 1000),
                author=profiles.get(pk=random.randint(1, profiles_amount)),
                created_at=str(fake.date_between(datetime(2000, 1, 1), datetime(2024, 12, 31)))
            )
            q.save()
            q.tags.set([tags.get(pk=random.randint(1, tags_count)) for i in range(2)])
            questions.append(q)

        questions = Question.objects
        questions_amount = questions.count()

        answers = [
            Answer(
                question=questions.get(pk=random.randint(1, questions_amount)),
                content=fake.text(max_nb_chars=512),
                author=profiles.get(pk=random.randint(1, profiles_amount)),
                likes=random.randint(0, 1000),
                created_at=str(fake.date_between(datetime(2000, 1, 1), datetime(2024, 12, 31)))
            )
            for i in range(answers_size)
        ]

        Answer.objects.bulk_create(answers)
        answers = Answer.objects
        answers_amount = answers.count()

        question_likes = [
            QuestionLike(
                author=profiles.get(pk=random.randint(1, profiles_amount)),
                question=questions.get(pk=random.randint(1, questions_amount)),
                like=random.randint(0, 1)
            )
            for i in range(likes_size // 2)
        ]

        QuestionLike.objects.bulk_create(question_likes)

        answer_likes = [
            AnswerLike(
                author=profiles.get(pk=random.randint(1, profiles_amount)),
                answer=answers.get(pk=random.randint(1, answers_amount)),
                like=random.randint(0, 1)
            )
            for i in range(likes_size // 2)
        ]

        AnswerLike.objects.bulk_create(answer_likes)
        print(datetime.now())

