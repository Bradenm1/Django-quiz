from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'triviaQuiz'
urlpatterns = [
    path('', views.IndexView.as_view(), name='home_page'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('highscores/', views.HighScoresView.as_view(), name='highscores'),
    path('create-tournament/', views.CreateTournamentView.as_view(), name='create_tournament'),
    path('delete-tournament/', views.DeleteTournamentView.as_view(), name='deleteTournament'),
    path('active-deactivate/', views.ActivateOrDeactivateTournamentView.as_view(), name='activate_or_deactivate_Tournament'),
    path('reset-Session/', views.ResetSessionView.as_view(), name='reset_Session'),
    path('show-tournament-questions/', views.ShowTournamentQuestionsView.as_view(), name='show_tournament_questions'),
    url(r'^quiz/(?P<slug>[\w-]+)/$', views.quiz, name='quiz')
]