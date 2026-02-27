from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_home, name='main_home'),
    path('co/', views.home, name='home'),
    path('practice/<slug:practice_slug>/',                              views.practice_index, name='practice_index'),
    path('practice/<slug:practice_slug>/question/<int:question_id>/',  views.question,       name='question'),
    path('practice/<slug:practice_slug>/results/',                      views.results,        name='results'),
]
