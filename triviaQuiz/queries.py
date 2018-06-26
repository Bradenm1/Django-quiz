from triviaQuiz.models import Tournament, Question, QuestionAnswer, QuestionIncorrect, TournamentScore, UserProgress
from django.shortcuts import render
from random import shuffle
#from triviaQuiz.decorators import is_admin
import threading

# Command Pattern
class Command():
    def __init__(self, obj):
        """ Constructor
        
        Arguments:
            obj {A inherited objectes of this class} -- The class to be executed
        """

        self._obj = obj

    def execute(self, request, tournament):
        """ The execute function for the inherited objectes
        
        Arguments:
            request {Request} -- The request for the session
        
        Raises:
            NotImplementedError -- Add code here
        """

        raise NotImplementedError()

class PostCommand(Command):
    def execute(self, request, tournament):
        return self._obj.post_request(request, tournament)

class GetCommand(Command):
    def execute(self, request, tournament):
        return self._obj.get_request(request, tournament)

class CompletedCommand(Command):
    def execute(self, request, tournament):
        return self._obj.completed_request(request, tournament)

class QuizTypeReceiver():
    def get_request(self, request, tournament):
        """ The get request for viewing a question
        
        Arguments:
            request {Request} -- The current request for the session
        
        Returns:
            [render] -- Returns a rendered screen for the user
        """

        # Get the users current tournament
        tournament = UserSessionCache().getInstance().get_current_tournament()
        # Get the users session
        session = UserSessionCache().getInstance().get_session_session()
        # Get all the questions for the tournament
        questions = tournament.question_set.all()
        # Get the questions awnser
        answer = QuestionAnswer.objects.get(question=questions[session])
        # Get the incorrect answers
        incorrectAnswers = QuestionIncorrect.objects.filter(question=questions[session])
        # Get users current posititon in the question
        request.session['session'] = session
        # Get the users current score
        request.session['result'] = UserSessionCache().getInstance().get_user_progress().result
        # Get a randomized list given the answer and the incorrect answers
        options = Quiz().randomizeQuestions(answer, incorrectAnswers)
        context = {'tournament' : tournament, "quesiton" : questions[session], "options" : options}
        return render(request, 'quiz.html', context)

    def post_request(self, request, tournament):
        """ The post request for viewing a question
        
        Arguments:
            request {Request} -- The current request for the session
        
        Returns:
            [render] -- Returns a rendered screen for the user
        """

        # Get the users current tournament
        tournament = UserSessionCache().getInstance().get_current_tournament()
        user = request.user
        questions = tournament.question_set.all()
        userScore = request.session.get('result')
        answer = request.POST['selectOption']
        # Try get the users answer
        if (answer == 'null'): return self.get_request(request, tournament)
        getUserAnswer = ErrorHandling().try_get_answer(answer)
        # Check if page is missmatched
        if (not QuizClientMissMatch().getInstance().session_vaild()):
            # Take th uer to the next question
            context = Quiz().nextSubmitQuestion(tournament, user, userScore, getUserAnswer, questions)
            # Get the users pervious session
            userSession = request.session.get('session')
            # Get the users current session
            session = UserSessionCache().getInstance().get_session_progress()
            # Increment the users session
            session.session = int(userSession) + 1
            session.save()
        else:
            # Don't let the user go the next question
            context = Quiz().stayOnQuestion(tournament, getUserAnswer, questions)
        
        return render(request, 'answer.html', context)

    def completed_request(self, request, tournament):
        # Get the users stored tournament score
        tournamentScore = UserSessionCache().getInstance().get_user_progress()
        context = {'score' : tournamentScore.result}
        return render(request, 'completed.html', context)

class QuizTypeClient():
    def __init__(self):
        """ The constructor """

        self._receiver = QuizTypeReceiver()

    def run(self, request):
        requestType = {"GET" : GetCommand(self._receiver), "POST" : PostCommand(self._receiver)}
        # Get the users session
        session = UserSessionCache().getInstance().get_session_progress()
        # Check to see if the user has a missmatch
        QuizClientMissMatch().getInstance().setUp(session.session, request.session.get('session'))
        # Get the current tournament the user is on
        tournament = UserSessionCache().getInstance().get_current_tournament()
        # Check if the tournament is completed
        if (session.isCompleted()):
            # Run completed tournament code
            return CompletedCommand(self._receiver).execute(request=request, tournament=tournament)
        else:
            # Run showing question/answer code
            return requestType[request.method].execute(request=request, tournament=tournament)

# Singleton Pattern
class UserSessionCache():
    # The locking for the singleton
    _singletonLock = threading.Lock()
    # The global instance of the singleton
    _instance = None

    def setUp(self, *args, **kwargs):
        """ The setUp for the singleton instance """

        # Get the current request
        self.request = kwargs.get('request', None)
        # Get the current user
        self.user = kwargs.get('user', None)
        # Get the current tournament if any
        self.currentTournament = kwargs.get('tournament', None)
        # Check if user has has been in the tournament yet, if not created tables which will be used
        if (self.currentTournament): ErrorHandling().user_has_session(self.currentTournament, user=self.user)
        # Get the users progress
        self.userProgress = ErrorHandling().try_get_user_progress(tournament=self.currentTournament, user=self.user)
        # Get the users session
        self.userSession = ErrorHandling().try_get_user_session(tournament=self.currentTournament, user=self.user)

    def get_request(self):
        """ Gets a instance of the saved request
        
        Returns:
            Request -- current pages request
        """

        return self.request

    def get_user(self):
        """ Gets a instance of the logged-in uer
        
        Returns:
            User -- The user
        """

        return self.user

    def get_user_progress(self):
        """ Gets the users results in the current tournament
        
        Returns:
            TournamentScore -- The tournament score
        """

        return self.userProgress

    def get_session_progress(self):
        """ Get the current session
        
        Returns:
            UserProgress -- The users progress in the tournament
        """

        return self.userSession

    def get_session_session(self):
        """ The current index of the user in the tournament
        
        Returns:
            Integer -- Where the user is in the tournament
        """

        return self.get_session_progress().session

    def get_current_tournament(self):
        """ Returns the users current tournament
        
        Returns:
            Tournament -- The current tournament
        """

        return self.currentTournament

    @staticmethod
    def getInstance(*args, **kwargs):
        """ Singleton
        
        Returns:
            UserSessionCache -- An instance of APICaller object
        """
        if not UserSessionCache._instance:
            with UserSessionCache._singletonLock:
                if not UserSessionCache._instance:
                    UserSessionCache._instance = UserSessionCache()
                    UserSessionCache._instance.setUp(*args, **kwargs)
        return UserSessionCache._instance

# Singleton Pattern
class QuizClientMissMatch():
    _singletonLock = threading.Lock()
    _instance = None

    def setUp(self, clientSession, clientPastSession):
        self.clientSession = clientSession
        self.clientPastSession = clientPastSession

    def session_vaild(self):
        if (self.clientSession == self.clientPastSession):
            return False
        return True

    @staticmethod
    def getInstance():
        """ Singleton
        
        Returns:
            APICaller -- An instance of APICaller object
        """
        if not QuizClientMissMatch._instance:
            with QuizClientMissMatch._singletonLock:
                if not QuizClientMissMatch._instance:
                    QuizClientMissMatch._instance = QuizClientMissMatch()
        return QuizClientMissMatch._instance

# Template Pattern
class GetTournaments():
    def __init__(self, tournaments, user):
        """ The GetTournaments template design pattern 
            for getting information related to tournaments
        
        Arguments:
            tournaments {Tournament} -- The tournaments
            user {User} -- The logged-in user
        """

        self.tournaments = tournaments
        self.user = user

    def get_infomration(self):
        """ The code to be executed by the templates
        
        Returns:
            List -- The list of the tournaments
        """

        # Filter all sessions for a user
        sessions = UserProgress.objects.filter(user=self.user)
        # Loop though all sessions
        for session in sessions:
            if (self.filter_condition(session)):
                self.body_code(session)
        # Returns all touraments
        return self.tournaments

    def filter_condition(self, session):
        """ The filter condition to use
        
        Arguments:
            session {Session} -- The users session
        
        Raises:
            NotImplementedError -- Please add code here
        """

        raise NotImplementedError()

    def body_code(self, session):
        """ The body which will run for the template
        
        Arguments:
            session {Session} -- The users session
        
        Raises:
            NotImplementedError -- Please add code here
        """

        raise NotImplementedError()

class NonCompletedTournaments(GetTournaments):
    def filter_condition(self, session):
        # Check if session is completed
        return session.isCompleted()

    def body_code(self, session):
        self.tournaments = self.tournaments.exclude(pk=session.tournament.pk)

class CompletedTournaments(GetTournaments):
    def filter_condition(self, session):
        # Check if session is completed
        return session.isCompleted()

    def body_code(self, session):
        self.tournaments.append(session.tournament)

class MissedTournaments(GetTournaments):
    def filter_condition(self, session):
        # No condition
        return True

    def body_code(self, session):
        self.tournaments = self.tournaments.exclude(pk=session.tournament.pk, active=False)

class Quiz():

    def nextSubmitQuestion(self, tournament, user, userScore, getUserAnswer, questions):
        correct = False
        # Get the current users session
        session = UserSessionCache().getInstance().get_session_session()
        # Get the answer for the pervious question
        awnser = QuestionAnswer.objects.get(question=questions[session])
        # Check if that answer was correct
        if (getUserAnswer == awnser):
            correct = True
            score = TournamentScore.objects.get(tournament=tournament, user=user)
            score.result = int(userScore) + 1
            score.save()
        # Show the current questions options
        question = questions[session]
        # Increment the users session to be the next question
        return {'tournament' : tournament, 'question' : question, 'answer' : awnser, 'user_answer' : getUserAnswer, 'was_correct' : correct}

    def stayOnQuestion(self, tournament, getUserAnswer, questions):
        correct = False
        # Get the current users session
        session = UserSessionCache().getInstance().get_session_session()
        # Get the answer for the pervious question
        awnser = QuestionAnswer.objects.get(question=questions[session - 1])
        # Check if that answer was correct
        if (getUserAnswer == awnser):
            correct = True
        # Show the previous questions options
        question = questions[session - 1]
        return {'tournament' : tournament, 'question' : question, 'answer' : awnser, 'user_answer' : getUserAnswer, 'was_correct' : correct}

    def randomizeQuestions(self, answer, incorrectAnswers):
        """ Randomizes question options
        
        Arguments:
            answer {QuestionAnswer} -- The correct answer
            incorrectAnswers {List} -- The incorrect answers
        
        Returns:
            List -- The questions randomized
        """

        # Put incorrect answers into the list
        questions = ([question for question in incorrectAnswers])
        # Put correct answer into the list
        questions.append(answer)
        # Shuffle the list
        shuffle(questions)
        return questions

class TournamentStats():

    def __init__(self, user):
        """ Constructor
        
        Arguments:
            user {User} -- The user to use the stats for
        """

        self.user = user

    def getNumberOfTournamentsParticipated(self):
        """ The tournaments the user has entered into
        
        Returns:
            Integer -- The tournaments the user has entered into
        """

        return UserProgress.objects.filter(user=self.user).count()

    def getTotalCorrect(self):
        """ Gets the total correct answers for all tournaments
        
        Returns:
            Integer -- The sum total results of all the users tournamets
        """

        # Set total correct to zero by default
        total = 0
        # Get the all the tournaments scores for the user
        total_correct = TournamentScore.objects.filter(user=self.user)
        # Loop and append the score to the total
        for amount in total_correct:
            total += amount.result
        # Return the total
        return total

class AdminTools():
    """ The admin tools """

    def __init__(self, user):
        """ Constructor Admin user to use the admin tools """
        self.user = user

    #@is_admin
    def deleteTournament(self, tournament):
        tournament.delete()

    #@is_admin
    def resetScore(self, tournament, user):
        # Delete the tournament the user created
        TournamentScore.objects.get(tournament=tournament, user=user).resetScore()
        UserProgress.objects.get(tournament=tournament, user=user).resetSession()

class ErrorHandling():
    """ The error handling class """

    def try_get_user_session(self, tournament, user):
        try:
            return UserProgress.objects.get(user=user, tournament=tournament)
        except UserProgress.DoesNotExist:
            return None

    def try_get_user_progress(self, tournament, user):
        try:
            return TournamentScore.objects.get(tournament=tournament, user=user)
        except TournamentScore.DoesNotExist:
            return None

    def user_has_session(self, tournament, user):
        try:
            # Check is user has entered the tournament yet, returns an error if it does not exist
            TournamentScore.objects.get(tournament=tournament, user=user)
        except TournamentScore.DoesNotExist:
            # If the user has not entered the tournament yet, created the data needed to hold it's information
            TournamentScore.objects.create(result=0, tournament=tournament, user=user)
            UserProgress.objects.create(session=0, tournament=tournament, user=user)

    def tournament_exists(self, slug):
        # Check if tournament exists
        try:
            return Tournament.objects.get(slug=slug)
        except Tournament.DoesNotExist:
            return None

    def try_get_answer(self, awnser):
        # Check if answer exists in the answer table
        try:
            return QuestionAnswer.objects.get(pk=awnser) 
        except QuestionAnswer.DoesNotExist:
            return QuestionIncorrect.objects.get(pk=awnser)
        except QuestionIncorrect.DoesNotExist:
            return None