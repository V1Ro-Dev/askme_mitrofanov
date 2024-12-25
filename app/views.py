import jwt
import time
import json
from cent import Client, PublishRequest
from django.contrib import auth
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.views.decorators.http import require_POST
from app import models
from app.forms import LoginForm, SignupForm, SettingsForm, AskForm, AnswerForm

client = Client(settings.CENTRIFUGO_API_URL, settings.CENTRIFUGO_API_KEY)


def get_centrifugo_data(user_id, channel):
    ws_url = settings.CENTRIFUGO_WS_URL
    secret = settings.CENTRIFUGO_SECRET
    token = jwt.encode({"sub": str(user_id), "exp": int(time.time()) + 10 * 60}, secret, algorithm="HS256")
    return {
        'centrifugo': {
            'token': token,
            'url': ws_url,
            'channel': channel
        }
    }


def paginate(object_list, request, per_page=3):
    paginator = Paginator(object_list, per_page)
    page = request.GET.get('page', 1)
    try:
        paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        raise Http404("Page not found")
    return paginator.page(page)


def index(request):
    questions = paginate(models.Question.objects.get_new_questions(), request)
    return render(request, 'index.html',
                  context={'questions': questions,
                           'page_obj': questions,
                           'tags': models.Tag.objects.get_popular_tags(),
                           'members': models.Profile.objects.get_popular_profiles()}
                  )


def question(request, question_id):
    question_item = get_object_or_404(models.Question, id=question_id)
    answers = paginate(models.Answer.objects.get_answers(question_id), request)

    is_author = request.user == question_item.author.user

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        ans_form = AnswerForm(request.user, question_id, request.POST)
        if ans_form.is_valid():
            ans = ans_form.save()

            request = PublishRequest(channel=f"question_{question_id}", data=model_to_dict(ans))
            client.publish(request)

            redirect_url = reverse('question', args=[question_id]) + f'?page={1}'
            return redirect(redirect_url)
    else:
        ans_form = AnswerForm(request.user, question_id)
    return render(request, 'question.html',
                  context={'question': question_item,
                           'answers': answers,
                           'page_obj': answers, 'tags': models.Tag.objects.get_popular_tags(),
                           'members': models.Profile.objects.get_popular_profiles(),
                           'is_author': is_author,
                           'form': ans_form,
                           **get_centrifugo_data(request.user.id, f"question_{question_id}")}
                  )


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(request.GET.get("continue", "index"))
            else:
                login_form.add_error(None, 'Incorrect username or password')
    else:
        login_form = LoginForm()
    return render(request, 'login.html',
                  context={'tags': models.Tag.objects.get_popular_tags(),
                           'members': models.Profile.objects.get_popular_profiles(),
                           'form': login_form}
                  )


@login_required
def logout(request):
    auth.logout(request)
    return redirect(request.GET.get("continue", "index"))


def signup(request):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST, request.FILES)
        if signup_form.is_valid():
            user = signup_form.save()
            auth.login(request, user)
            return redirect('index')
    else:
        signup_form = SignupForm()
    return render(request, 'signup.html',
                  context={'tags': models.Tag.objects.get_popular_tags(),
                           'members': models.Profile.objects.get_popular_profiles(),
                           'form': signup_form}
                  )


@login_required()
def profileEdit(request):
    if request.method == 'POST':
        settings_form = SettingsForm(request.user, request.POST, request.FILES, instance=request.user)
        if settings_form.is_valid():
            user = settings_form.save()
            auth.login(request, user)
            return redirect('settings')
    else:
        settings_form = SettingsForm(request.user, instance=request.user)
    return render(request, 'settings.html',
                  context={'tags': models.Tag.objects.get_popular_tags(),
                           'members': models.Profile.objects.get_popular_profiles(),
                           'form': settings_form}
                  )


def ask(request):
    if request.method == 'POST':
        ask_form = AskForm(request.user, request.POST)
        if ask_form.is_valid():
            question = ask_form.save()
            return redirect('question', question_id=question.id)
    else:
        ask_form = AskForm(request.user)
    return render(request, 'ask.html',
                  context={'tags': models.Tag.objects.get_popular_tags(),
                           'members': models.Profile.objects.get_popular_profiles(),
                           'form': ask_form}
                  )


def tag(request, tag_name):
    get_object_or_404(models.Tag, name=tag_name)
    questions = paginate(models.Question.objects.get_questions_by_tag(tag_name), request)
    return render(request, 'tag.html',
                  context={'tag_name': tag_name,
                           'questions': questions,
                           'page_obj': questions,
                           'tags': models.Tag.objects.get_popular_tags(),
                           'members': models.Profile.objects.get_popular_profiles()}
                  )


def hot(request):
    questions = paginate(models.Question.objects.get_hot_questions(), request)
    return render(request, 'index.html',
                  context={'questions': questions,
                           'page_obj': questions,
                           'tags': models.Tag.objects.get_popular_tags(),
                           'members': models.Profile.objects.get_popular_profiles()}
                  )


@require_POST
@login_required(redirect_field_name='continue')
def questionLike(request):
    query_params = json.loads(request.body)
    profile = get_object_or_404(models.Profile, user=request.user)
    question = get_object_or_404(models.Question, pk=query_params['question_id'])
    like, created_at = models.QuestionLike.objects.get_or_create(author=profile, question=question)

    if not created_at:
        like.delete()
        question.likes -= 1
        liked = False
    else:
        question.likes += 1
        liked = True
    question.save()

    return JsonResponse({'likes_count': question.likes, 'liked': liked})


@require_POST
@login_required(redirect_field_name='continue')
def answerLike(request):
    query_params = json.loads(request.body)
    profile = get_object_or_404(models.Profile, user=request.user)
    question = get_object_or_404(models.Question, pk=query_params['question_id'])
    answer = get_object_or_404(models.Answer, pk=query_params['answer_id'], question=question)
    like, created_at = models.AnswerLike.objects.get_or_create(answer=answer, author=profile)

    if not created_at:
        like.delete()
        answer.likes -= 1
        liked = False
    else:
        answer.likes += 1
        liked = True
    answer.save()

    return JsonResponse({'likes_count': answer.likes, 'liked': liked})


@require_POST
@login_required(redirect_field_name='continue')
def correctAnswer(request):
    query_params = json.loads(request.body)
    question = get_object_or_404(models.Question, pk=query_params['question_id'])
    answer = get_object_or_404(models.Answer, pk=query_params['answer_id'], question=question)

    if answer.correct:
        answer.correct = False
    else:
        answer.correct = True
    answer.save()
    return JsonResponse({'correct': answer.correct})
