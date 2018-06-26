class QuizStrategy():
    def __init__(self):
        """ Constructor """
        pass

    def execute(self, request, tournament, session, questions, answer):
        pass

class QuizStrategySubmittedAnswer():

    def execute(self):
        pass

class QuizStrategyViewingQuestion():

    def execute(self):
        pass
    
class QuizStrategyCompletedTournament():

    def execute(self):
        pass


class GetTournaments():
    def __init__(self):
        """ Constructor """
        pass

    def execute(self, tournaments, sessions):
        for session in sessions:
            self.strategy(tournaments, session)
        return tournaments

    def strategy(self, tournaments, session):
        pass

class GetTournamentsCompleted(GetTournaments):

    def strategy(self, tournaments, session):
        if (session.isCompleted()):
            tournaments.append(session.tournament)

class GetTournamentsNonCompleted(GetTournaments):
    
    def strategy(self, tournaments, session):
        if (session.isCompleted()):
            tournaments = tournaments.exclude(pk=session.tournament.pk)

class GetTournamentsMissed(GetTournaments):
    
    def strategy(self, tournaments, session):
        tournaments = tournaments.exclude(pk=session.tournament.pk)