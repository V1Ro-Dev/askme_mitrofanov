from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/edit/', views.settings, name='settings'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('questionLike/', views.questionLike, name='questionLike'),
    path('answerLike/', views.answerLike, name='answerLike'),
    path('correctAnswer/', views.correctAnswer, name='correctAnswer'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)