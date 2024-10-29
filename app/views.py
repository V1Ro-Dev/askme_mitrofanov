from django.shortcuts import render
from django.core.paginator import Paginator

QUESTIONS = [
        {
            'id': i,
            'title': f'question {i}',
            'content': f'long long lore {i}'
        } for i in range(10)
    ]


def paginate(objects, page, per_page=3):
    paginator = Paginator(objects, per_page)
    return paginator.page(page)


def index(request):
    page = request.GET.get('page', 1)
    return render(request, 'index.html', context={'questions': paginate(QUESTIONS, page)})


def question(request, question_id):
    item = QUESTIONS[question_id]
    return render(request, 'question.html', context={'question': item})


def login(request):
    return render(request, 'login.html')


def registration(request):
    return render(request, 'registration.html')


def settings(request):
    return render(request, 'settings.html')


def tag(request):
    return render(request, 'tag.html')


def ask(request):
    return render(request, 'ask.html')
