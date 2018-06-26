from django import forms
from triviaQuiz.models import Tournament

class CreateTournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = {'name' : 'Tournament Name:',
                'startDate' : 'Start Date:', 
                'endDate' : 'Start Date:',
                'category' : 'Categories',
                'difficulty' : 'Difficulty',
                'active' : 'Active'
            }