from datetime import datetime
from django.core.management.base import BaseCommand
from app.models import Question, Answer, Profile, AnswerLike, QuestionLike, Tag, User
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        print('started at:', datetime.now())
        ratio = options['ratio']

        tags_size = ratio
        likes_size = ratio * 200
        questions_size = ratio * 10
        profiles_size = ratio
        answers_size = ratio * 100

        usernames = [f'{fake.user_name()}_{i}' for i in range(profiles_size)]
        emails = [f'{username}@mail.ru' for username in usernames]

        users = [User(username=username, email=email, password=fake.password()) for username, email in
                 zip(usernames, emails)]
        User.objects.bulk_create(users)

        users = User.objects.all()[:profiles_size]
        profiles = [Profile(user=user) for user in users]

        Profile.objects.bulk_create(profiles)
        profiles = Profile.objects

        print('profiles ended at:', datetime.now())

        tags = [Tag(name=f'{fake.word()}{i}') for i in range(tags_size)]

        Tag.objects.bulk_create(tags)
        tags = Tag.objects

        print('tags ended at:', datetime.now())

        questions_lst = [
            Question(
                title=fake.sentence(nb_words=3),
                content=fake.text(max_nb_chars=512),
                author=profiles.get(pk=random.randint(1, profiles_size)),
                likes=0,
                amount_of_answers=0,
                created_at=str(fake.date_between(datetime(2000, 1, 1), datetime(2024, 12, 31)))
            )
            for i in range(questions_size)
        ]

        Question.objects.bulk_create(questions_lst)
        for question in questions_lst:
            question.tags.set([tags.get(pk=random.randint(1, tags_size)) for i in range(random.randint(1, 5))])

        questions = Question.objects

        print('questions ended at:', datetime.now())

        answers_lst = []
        for i in range(answers_size):
            ind = random.randint(1, questions_size)
            ans = Answer(
                question=questions.get(pk=ind),
                content=fake.text(max_nb_chars=512),
                author=profiles.get(pk=random.randint(1, profiles_size)),
                likes=0,
                created_at=str(fake.date_between(datetime(2000, 1, 1), datetime(2024, 12, 31)))
            )
            questions_lst[ind - 1].amount_of_answers += 1
            answers_lst.append(ans)

        Question.objects.bulk_update(questions_lst, ['amount_of_answers'])
        Answer.objects.bulk_create(answers_lst)
        answers = Answer.objects

        print('answers ended at:', datetime.now())

        question_likes = []
        question_likes_set = set()
        for i in range(likes_size // 2):
            ind = random.randint(1, questions_size)
            ind_author = random.randint(1, profiles_size)
            like = random.randint(0, 1)
            while (ind, ind_author) in question_likes_set:
                ind = random.randint(1, questions_size)
                ind_author = random.randint(1, profiles_size)
            question_like = QuestionLike(
                author=profiles.get(pk=ind_author),
                question=questions.get(pk=ind),
                like=like
            )
            if question_like.like == 1:
                questions_lst[ind - 1].likes += 1
            question_likes_set.add((ind, ind_author))
            question_likes.append(question_like)

        Question.objects.bulk_update(questions_lst, ['likes'])
        QuestionLike.objects.bulk_create(question_likes)

        print('question likes ended at:', datetime.now())

        answer_likes = []
        ans_likes_set = set()
        for i in range(likes_size // 2):
            ind_ans = random.randint(1, answers_size)
            ind_author = random.randint(1, profiles_size)
            like = random.randint(0, 1)
            while (ind_ans, ind_author) in ans_likes_set:
                ind_ans = random.randint(1, answers_size)
                ind_author = random.randint(1, profiles_size)

            ans_like = AnswerLike(
                author=profiles.get(pk=ind_author),
                answer=answers.get(pk=ind_ans),
                like=like
            )
            if ans_like.like == 1:
                answers_lst[ind_ans - 1].likes += 1
            ans_likes_set.add((ind_ans, ind_author))
            answer_likes.append(ans_like)

        Answer.objects.bulk_update(answers_lst, ['likes'])
        AnswerLike.objects.bulk_create(answer_likes)

        print('ended at:', datetime.now())
