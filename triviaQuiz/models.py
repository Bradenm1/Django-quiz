from django.db import models
from django.conf import settings
from django.urls import reverse
from . import services
import datetime

# Create your models here.

class TournamentQuerySet(models.query.QuerySet):
    def getHighScores(self):
        """ Gets a list of all the highscores for each tournament
    
        Returns:
            List -- All highscores
        """

        highScores = list()
        # Get all the results
        results = Tournament.customManager.getAllResults()
        # Loop though all the scores
        for scores in results.values():
            # Check if score is not null
            if scores:
                # Assign highscore to the frst score
                highScore = scores[0]
                # Loop though all the reults in the scores
                for result in scores:
                    # Check if the other scores are high then the first
                    if (result.result > highScore.result):
                        # If so assign it as the new high score
                        highScore = result
                # Append tha highscore to the other scores
                highScores.append(highScore)
        return highScores

    def getActiveTournaments(self):
        """ Gets a list of all active tournaments
        
        Returns:
            List -- All tournaments
        """

        tournaments = list()
        # Loop though all the tournaments
        for tournament in Tournament.objects.all():
            # Check if it's active
            if(tournament.active):
                # If so append it to the list
                tournaments.append(tournament)
        return tournaments

    def getCreationResult(self, tournament):
        """ Get a list of all the questions in the tournament
        
        Arguments:
            tournament {Tournament} -- The tournament
        
        Returns:
            List -- List of the questions
        """

        all_questions = list()
        # Loop though all questions in the tournament
        for question in tournament.question_set.all():
            # Get the answer for each tournament
            answer = QuestionAnswer.objects.get(question=question)
            # Get the category
            category = tournament.category
            # Check if the category is empty
            if (not tournament.category):
                category = 'Random'
            # Add the question to the list
            all_questions.append([category, tournament.getDifficulty(), question.question, answer.option])
        return all_questions

    def getAllResults(self):
        """ Get all the results for every tournament
        
        Returns:
            TournametScore -- All tournamentscores
        """

        AllScores = dict()
        # Get all tournaments
        tournaments = Tournament.objects.all()
        # Loop though all tournaments
        for tournament in tournaments:
            # Get all tournament scores
            tournmentScores = TournamentScore.objects.filter(tournament=tournament)
            # Loop though all the scores and append it to a list
            scores = ([score for score in tournmentScores])
            # Addd the sources to the dict with the tournament being the key
            AllScores[tournament.pk] = scores
        return AllScores

    def progress(self, user): 
        """ Gets all progress for a user
        
        Arguments:
            user {User} -- User to use
        
        Returns:
            List -- list of values as progress
        """

        values = list()
        for tournament in self.active():
            # Get all active sessions for the user
            active_sessions = UserProgress.objects.filter(tournament=tournament, user=user)
            # Loop though all active sessions
            for session in active_sessions:
                if (not session.isCompleted()):
                    # Append value to list and times by 10 to give a percentage from 100%
                    values.append(session.getProgress())
        return values

    def future(self):
        return self.filter(startDate__gte=datetime.datetime.now(), active=True)

    def missed(self):
        return self.filter(endDate__lte=datetime.datetime.now(), active=True)

    def active(self):
        return self.filter(startDate__lte=datetime.datetime.now(), endDate__gte=datetime.datetime.now(), active=True)

class TournamentManager(models.Manager):
    def getHighScores(self):
        return self.get_query_set().getHighScores()
        
    def getActiveTournaments(self):
        return self.get_query_set().getActiveTournaments()

    def getCreationResult(self, tournament):
        return self.get_query_set().getCreationResult(tournament=tournament)

    def get_query_set(self):
        return TournamentQuerySet(self.model, using=self._db)

    def getAllResults(self):
        return self.get_query_set().getAllResults()

    def progress(self, user):
        return self.get_query_set().progress(user)

    def future(self):
        return self.get_query_set().future()

    def missed(self):
        return self.get_query_set().missed()

    def active(self):
        return self.get_query_set().active()

# Tournament Table
class Tournament(models.Model):
    DifficultyENUM = (('1', 'easy'),('2', 'medium'),('3', 'hard'))
    CategoryENUM = services.get_categories()
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)
    active = models.BooleanField(default=True)
    startDate = models.DateField()
    endDate = models.DateField()
    category = models.CharField(max_length=255, blank=True, null=True, choices=CategoryENUM)
    difficulty = models.CharField(max_length=10, blank=True, null=True, choices=DifficultyENUM)

    def get_absolute_url(self):
        """ The path for viewing this tournament """

        return reverse('triviaQuiz:quiz', kwargs={'slug' : self.slug})

    def getDifficulty(self):
        """ Returns difficulty for a tournament
        
        Returns:
            String -- The difficulty
        """

        difficulty = {'1' : 'Easy', '2' : 'Medium', '3' : 'Hard'}
        if self.difficulty in difficulty:
            return difficulty[self.difficulty]
        return 'Random'

    def isTournamentEmpty(self):
        """ Checks if a tournament has any questions
        
        Returns:
            Boolean -- Empty or not
        """

        nQuestions = Question.objects.filter(tournament=self.id).count()
        if (nQuestions <= 0):
            return True
        return False

    def __str__(self):
        return "Tournament: %s" % (self.name)

    # Set default manager
    objects = models.Manager()
    # Set custom manager
    customManager = TournamentManager()

# TournamentScore Table
# Keep track of the scores for a given user in a tournament
class TournamentScore(models.Model):
    result = models.IntegerField() # The current score for the user
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def resetScore(self):
        """ Resets the results """

        self.result = 0
        self.save()

    def appendScore(self):
        """ Increments the score """

        self.result += 1
        self.save()

    def __str__(self):
        return "result: %s, Tournament: %s, User: %s" % (self.result, self.tournament, self.user)

# The users progress on a tournament
class UserProgress(models.Model):
    session = models.IntegerField() # Question index the user is on
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def resetSession(self):
        """ Rests the session """

        self.session = 0
        self.save()

    def getProgress(self):
        """ Gets the progress for a tournament
        
        Returns:
            Integer -- The progress
        """

        nQuestions = Question.objects.filter(tournament=self.tournament.pk).count()
        return self.session * nQuestions

    def isCompleted(self):
        """ Check is the user has completed a tournament
        
        Returns:
            Boolean -- If is completed
        """

        nQuestions = Question.objects.filter(tournament=self.tournament.pk).count()
        if (self.session >= nQuestions): return True
        return False

    def appendScore(self):
        """ Increments the session """

        self.session += 1
        self.save()

    def __str__(self):
        return "Position: %s, Tournament: %s, User: %s" % (self.session, self.tournament, self.user)

# Question Table
# A question and have one answer
# A question can belong to 1 tournament, but tournaments have have multiable questions
class Question(models.Model):
    question = models.CharField(max_length=255) # Holds the question
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return "Question: %s" % (self.question)

# Question option
class QuestionOption(models.Model):
    option = models.CharField(max_length=255) # A answer to the question
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

# Answer to the questions
class QuestionAnswer(QuestionOption):

    def __str__(self):
        return "Answer: %s" % (self.option)

# Incorrect Answer to the questions
class QuestionIncorrect(QuestionOption):

    def __str__(self):
        return "Incorrect Answer: %s" % (self.option)