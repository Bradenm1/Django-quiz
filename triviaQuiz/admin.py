from django.contrib import admin

# Register your models here.
from .models import Tournament, Question, QuestionAnswer, QuestionIncorrect, TournamentScore, UserProgress

admin.site.register(Tournament)
admin.site.register(TournamentScore)
admin.site.register(Question)
admin.site.register(QuestionAnswer)
admin.site.register(QuestionIncorrect)
admin.site.register(UserProgress)