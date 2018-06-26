from triviaQuiz.forms import CreateTournamentForm
from . import models

class TournametToBuild():
    def __init__(self, name=None, startDate=None, endDate=None, category=None, difficulty=None, active=None):
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
        self.category = category
        self.difficulty = difficulty
        self.active = active

    def get_form_instance(self):
        return CreateTournamentForm(
            data={  'name' : self.name,
                    'startDate' : self.startDate,
                    'endDate' : self.endDate,
                    'category' : self.category,
                    'difficulty' : self.difficulty,
                    'active' : self.active,
                    'endDate' : self.endDate
        })
    
    def get_tournament_instance(self):
        form = self.get_form_instance()
        if form.is_valid():
            tournament = models.Tournament(**form.cleaned_data)
            tournament.save()
            return tournament
        return None

class TournamentBuilder:
    def set_name(self, value):
        pass

    def set_startDate(self, value):
        pass

    def set_endDate(self, value):
        pass

    def set_category(self, value):
        pass

    def set_difficulty(self, value):
        pass

    def set_active(self, value):
        pass

class Tournament(TournamentBuilder):
    def __init__(self):
        self.form = TournametToBuild()

    def set_name(self, value):
        self.form.name = value

    def set_startDate(self, value):
        self.form.startDate = value

    def set_endDate(self, value):
        self.form.endDate = value

    def set_category(self, value):
        self.form.category = value

    def set_difficulty(self, value):
        self.form.difficulty = value

    def set_active(self, value):
        self.form.active = value

    def get_form_instance(self):
        return self.form.get_form_instance()

    def get_tournament_instance(self):
        return self.form.get_tournament_instance()