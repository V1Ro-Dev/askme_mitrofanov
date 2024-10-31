import random

from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

TAGS = [{'name': 'Perl'},
        {'name': 'Python'},
        {'name': 'MySQL'},
        {'name': 'Django'},
        {'name': 'Mail.ru'},
        {'name': 'Firefox'}]

QUESTIONS = [
    {
        'id': i,
        'title': f'question {i}',
        'content': f'long long lore {i}',
        'tags': TAGS[0:3]
    } for i in range(20)
]

ANSWERS = [[0] * 10 for k in range(10)]
for i in range(10):
    for j in range(10):
        ANSWERS[i][j] = {
            'id': j,
            'content': f'Long long answer {j}'
        }

MEMBERS = [{'name': 'Mr. Freeman'},
           {'name': 'Dr. House'},
           {'name': 'Bender'},
           {'name': 'Walter White'},
           {'name': 'Sam'}]


def tag_selection(questions, tag_name):
    result = []
    for i in range(len(questions)):
        tags = questions[i]['tags']
        for j in range(len(tags)):
            if tag_name == tags[j]['name']:
                result.append(questions[i])
    return result


def get_question_by_id(question_id):
    for dic in QUESTIONS:
        if dic['id'] == question_id:
            return dic


def paginate(object_list, request, per_page=3):
    paginator = Paginator(object_list, per_page)
    page = request.GET.get('page', 1)
    try:
        paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(1)
    else:
        return paginator.page(page)


def index(request):
    page_obj = paginate(QUESTIONS, request)
    questions = paginate(QUESTIONS, request)
    return render(request, 'index.html',
                  context={'questions': questions, 'page_obj': page_obj, 'tags': TAGS, 'members': MEMBERS})


def question(request, question_id):
    list_of_answers = ANSWERS[question_id]
    page_obj = paginate(list_of_answers, request)
    answers = paginate(list_of_answers, request)
    question_item = get_question_by_id(question_id)
    return render(request, 'question.html',
                  context={'question': question_item, 'answers': answers, 'page_obj': page_obj, 'tags': TAGS,
                           'members': MEMBERS})


def login(request):
    return render(request, 'login.html', context={'tags': TAGS, 'members': MEMBERS})


def signup(request):
    return render(request, 'signup.html', context={'tags': TAGS, 'members': MEMBERS})


def settings(request):
    return render(request, 'settings.html', context={'tags': TAGS, 'members': MEMBERS})


def ask(request):
    return render(request, 'ask.html', context={'tags': TAGS, 'members': MEMBERS})


def tag(request, tag_name):
    questions = paginate(tag_selection(QUESTIONS, tag_name), request)
    page_obj = paginate(tag_selection(QUESTIONS, tag_name), request)
    return render(request, 'tag.html',
                  context={'tag_name': tag_name, 'questions': questions, 'page_obj': page_obj, 'tags': TAGS,
                           'members': MEMBERS})


def hot(request):
    page_obj = paginate(QUESTIONS, request)
    questions = paginate(QUESTIONS, request)
    return render(request, 'index.html',
                  context={'questions': questions, 'page_obj': page_obj, 'tags': TAGS, 'members': MEMBERS})
