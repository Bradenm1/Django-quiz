from django.test import TestCase
from triviaQuiz.models import Tournament, Question, QuestionAnswer, QuestionIncorrect, TournamentScore, UserProgress
from django.contrib.auth.models import User 
from django.urls import reverse
from django.test import Client
from . import builders
from . import queries
import datetime

class CreatCommonInstances():
    def create_common_tournament_instance(self):
        """ Creates a common tournament instance """
        tournmentBuilder = builders.Tournament()
        tournmentBuilder.set_name('Math Quiz')
        tournmentBuilder.set_startDate(datetime.date.today() + datetime.timedelta(days=1))
        tournmentBuilder.set_endDate(datetime.date.today() + datetime.timedelta(days=3))
        tournmentBuilder.set_category('23')
        tournmentBuilder.set_difficulty('1')
        tournmentBuilder.set_active(False)
        return tournmentBuilder.get_tournament_instance()

    def create_common_admin_user(self):
        """ Returns a created instance of a admin """
        admin = User.objects.create_user(username='admin', password='p@ssw0rd')
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        return admin

    def create_common_user(self):
        """ Returns a created instance of a user """
        return User.objects.create_user(username='test', password='p@ssw0rd')

    def login_as_common_admin(self, obj):
        """ Retun a common admin login """
        return obj.client.login(username="admin", password="p@ssw0rd")

    def login_as_common_user(self, obj):
        """ Return a common user login """
        return obj.client.login(username="test", password="p@ssw0rd")

# Create your tests here.
class TournamentsTestCase(TestCase):
    def setUp(self):
        """ Setup """ 
        self.tournament = CreatCommonInstances().create_common_tournament_instance()

    def test_tournamet_slug(self):
        """ Testing that a tournament slug, given the name is correctly made """
        self.assertEqual(self.tournament.slug, 'math-quiz-1')

    def test_tournamet_difficulty(self):
        """ Testing if getting a difficulty returns the correct result """
        self.assertEqual(self.tournament.getDifficulty(), 'Easy')

    def test_tournamet_no_questions(self):
        """ Testing if the method for checking if a you """
        self.assertEqual(self.tournament.isTournamentEmpty(), False)

    def test_get_absolute_url(self):
        """ Testing if it can get the absolute path """
        self.assertIsNotNone(self.tournament.get_absolute_url())

    def test_get_difficulty(self):
        """ Testing if the tournament returns the correct difficulty """
        difficulty = self.tournament.getDifficulty()
        self.assertEqual(difficulty, 'Easy')

    def test_get_name(self):
        """ Testing if tournment returns the correct name """
        self.assertEqual(self.tournament.name, 'Math Quiz')

    def test_get_to_string(self):
        """ Testing if tournment returns the correct toString """
        self.assertEqual(self.tournament.__str__(), 'Tournament: Math Quiz')

class QuestionsTestCase(TestCase):

    def setUp(self):
        """ SetUp """
        self.tournament = CreatCommonInstances().create_common_tournament_instance()
        self.question = Question.objects.create(
            question="Some Math Question", 
            tournament=self.tournament,
        )

    def get_question(self):
        """ Testing if question returns the correct toString """
        self.assertEqual(self.question.question, 'Some Math Question')

    def test_toString(self):
        """ Testing if question returns the correct toString """
        self.assertEqual(self.question.__str__(), 'Question: Some Math Question')

class QuestionAnswerTest(TestCase):
    def setUp(self):
        self.tournament = CreatCommonInstances().create_common_tournament_instance()
        self.question = Question.objects.create(
            question="Some Math Question", 
            tournament=self.tournament,
        )
        self.answer = QuestionAnswer.objects.create(
            option="A question", 
            question=self.question,
        )

    def test_toString(self):
        """ Testing if question answer returns the correct toString """
        self.assertEqual(self.answer.__str__(), 'Answer: A question')

class QuestionIncorrectTest(TestCase):
    def setUp(self):
        """ Setup """
        self.tournament = CreatCommonInstances().create_common_tournament_instance()
        self.question = Question.objects.create(
            question="Some Math Question", 
            tournament=self.tournament,
        )
        self.incorrect = QuestionIncorrect.objects.create(
            option="A Incorrect Question",
            question=self.question,
        )

    def test_toString(self):
        """ Testing if question incorrect returns the correct toString """
        self.assertEqual(self.incorrect.__str__(), 'Incorrect Answer: A Incorrect Question')

class CreateTournamentFormTest(TestCase):

    def test_setting_dates_normal(self):
        """ Test the fourm passes with normal data """
        formBuilder = builders.Tournament()
        formBuilder.set_name('Math Quiz')
        formBuilder.set_startDate(datetime.date.today() + datetime.timedelta(days=1))
        formBuilder.set_endDate(datetime.date.today() + datetime.timedelta(days=3))
        formBuilder.set_category('27')
        formBuilder.set_difficulty('1')
        formBuilder.set_active(False)
        self.assertEqual(formBuilder.get_form_instance().is_valid(), True)

    def test_setting_no_name(self):
        """ Test the form errors with no name """
        formBuilder = builders.Tournament()
        formBuilder.set_startDate(datetime.date.today() + datetime.timedelta(days=1))
        formBuilder.set_endDate(datetime.date.today() + datetime.timedelta(days=3))
        formBuilder.set_category('27')
        formBuilder.set_difficulty('1')
        formBuilder.set_active(False)
        self.assertEqual(formBuilder.get_form_instance().is_valid(), False)

    def test_setting_no_dates(self):
        """ Test the form errors with no name """
        formBuilder = builders.Tournament()
        formBuilder.set_name('Math Quiz')
        formBuilder.set_category('27')
        formBuilder.set_difficulty('1')
        formBuilder.set_active(False)
        self.assertEqual(formBuilder.get_form_instance().is_valid(), False)

    def test_setting_difficulty_out_of_bounds(self):
        """ Test the form errors with no name """
        formBuilder = builders.Tournament()
        formBuilder.set_name('Math Quiz')
        formBuilder.set_startDate(datetime.date.today() + datetime.timedelta(days=1))
        formBuilder.set_endDate(datetime.date.today() + datetime.timedelta(days=3))
        formBuilder.set_category('27')
        formBuilder.set_difficulty('5')
        formBuilder.set_active(False)
        self.assertEqual(formBuilder.get_form_instance().is_valid(), False)

    def test_setting_no_active(self):
        """ Test the form errors with no name """
        formBuilder = builders.Tournament()
        formBuilder.set_startDate(datetime.date.today() + datetime.timedelta(days=1))
        formBuilder.set_endDate(datetime.date.today() + datetime.timedelta(days=3))
        formBuilder.set_category('27')
        formBuilder.set_difficulty('5')
        formBuilder.set_active(False)
        self.assertEqual(formBuilder.get_form_instance().is_valid(), False)

    def test_setting_no_data(self):
        """ Test that the form errors out with no data """
        formBuilder = builders.Tournament()
        self.assertEqual(formBuilder.get_form_instance().is_valid(), False)

class UserViewsTest(TestCase):
    def setUp(self):
        """ Setup """
        self.tournament = CreatCommonInstances().create_common_tournament_instance()
        self.user = CreatCommonInstances().create_common_user()

    def test_enter_tournament(self):
        """ Test if a user can enter a tournament """
        self.client.login(username="test", password="p@ssw0rd")
        response = self.client.get(self.tournament.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_user_progress_created(self):
        """ Check if the users progress was created """
        user_login = CreatCommonInstances().login_as_common_user(self)
        self.client.get(self.tournament.get_absolute_url())
        user_progress_instance = UserProgress.objects.get(tournament=self.tournament, user=user_login)
        self.assertIsNotNone(user_progress_instance)

    def test_user_session_created(self):
        """ Check if the users progress was created """
        user_login = CreatCommonInstances().login_as_common_user(self)
        self.client.get(self.tournament.get_absolute_url())
        user_progress_instance = TournamentScore.objects.get(tournament=self.tournament, user=user_login)
        self.assertIsNotNone(user_progress_instance)

    def test_anwser_tournament_question(self):
        """ Check the user can answer a question """
        response = self.client.post(self.tournament.get_absolute_url(), data={ 'selectOption' : 0 })
        self.assertEqual(response.status_code, 302)

    def test_user_view_high_score(self):
        """ Check if the user can view high scores """
        response = self.client.get(reverse('triviaQuiz:highscores'))
        self.assertEqual(response.status_code, 302)

    def test_user_view_home_page(self):
        """ Check if the user can view high scores """
        response = self.client.get(reverse('triviaQuiz:home_page'))
        self.assertEqual(response.status_code, 302)

class AdminViewsTests(TestCase):

    def setUp(self):
        """ Setup a admin users """
        self.tournament = CreatCommonInstances().create_common_tournament_instance()
        self.admin = CreatCommonInstances().create_common_admin_user()

    def test_admin_view_create_tournament(self):
        """ Check if the staff can view the create tournament page """
        CreatCommonInstances().login_as_common_admin(self)
        response = self.client.get(reverse('triviaQuiz:create_tournament'))
        self.assertEqual(response.status_code, 200)

    def test_view_reset_session(self):
        """ Check if admin can reset session """
        CreatCommonInstances().login_as_common_admin(self)
        self.client.get(self.tournament.get_absolute_url())
        user_session_instance = UserProgress.objects.get(tournament=self.tournament, user=self.admin)
        user_session_instance.session = 2
        user_session_instance.save()
        self.client.post(reverse('triviaQuiz:reset_Session'), {'tournament_id' : self.tournament.slug})
        updated_instance = UserProgress.objects.get(tournament=self.tournament, user=self.admin)
        self.assertEqual(updated_instance.session, 0)

    def test_view_reset_tournament_score(self):
        """ Check if admin can reset session """
        CreatCommonInstances().login_as_common_admin(self)
        self.client.get(self.tournament.get_absolute_url())
        user_progress_instance = TournamentScore.objects.get(tournament=self.tournament, user=self.admin)
        user_progress_instance.result = 2
        user_progress_instance.save()
        self.client.post(reverse('triviaQuiz:reset_Session'), {'tournament_id' : self.tournament.slug})
        updated_instance = TournamentScore.objects.get(tournament=self.tournament, user=self.admin)
        self.assertEqual(updated_instance.result, 0)

class QuizClientMissMatchTest(TestCase):

    def session_vaild_missmatch(self):
        """ Check if there's a missmatch """
        client = queries.QuizClientMissMatch.getInstance()
        client.setUp(1, 2)
        self.assertEqual(client, False)

    def session_vaild_match(self):
        """ Check if there's a match """
        client = queries.QuizClientMissMatch.getInstance()
        client.setUp(1, 1)
        self.assertEqual(client, False)

class TournamentStatsTest(TestCase):
    
    def setUp(self):
        """ Setup """ 
        self.tournament = CreatCommonInstances().create_common_tournament_instance()
        self.user = CreatCommonInstances().create_common_user()
        self.stats = queries.TournamentStats(self.user)

    def test_try_get_user_session_tournament(self):
        """ Check if there's a session for the user """
        user_login = CreatCommonInstances().login_as_common_user(self)
        self.client.get(self.tournament.get_absolute_url())
        session = queries.ErrorHandling().try_get_user_session(user=user_login, tournament=self.tournament)
        self.assertIsNotNone(session)

    def test_get_number_of_tournaments_participated(self):
        """ Check the number of participated tournaments """
        value = self.stats.getNumberOfTournamentsParticipated()
        self.assertEqual(value, 0)

    def test_get_total_correct(self):
        """ Check the total correct answer """
        value = self.stats.getTotalCorrect()
        self.assertEqual(value, 0)

class ErrorHandlingClassTest(TestCase):
    
    def setUp(self):
        """ SetUp """
        self.tournament = CreatCommonInstances().create_common_tournament_instance()
        self.user = CreatCommonInstances().create_common_user()

    def test_try_get_user_session_empty(self):
        """ Check if returns none if empty """
        session = queries.ErrorHandling().try_get_user_session(user=None, tournament=None)
        self.assertEqual(session, None)

    def test_try_get_user_session_user(self):
        """ Check if returns none if empty given a user """
        session = queries.ErrorHandling().try_get_user_session(user=self.user, tournament=None)
        self.assertEqual(session, None)

    def test_try_get_user_session_tournament(self):
        """ Check if returns none if empty given a user """
        session = queries.ErrorHandling().try_get_user_session(user=None, tournament=self.tournament)
        self.assertEqual(session, None)

    def test_try_get_user_session(self):
        """ Check if returns session if given user and tournament """
        user_login = CreatCommonInstances().login_as_common_user(self)
        self.client.get(self.tournament.get_absolute_url())
        session = queries.ErrorHandling().try_get_user_session(user=user_login, tournament=self.tournament)
        self.assertIsNotNone(session)

    def test_try_get_user_progress_empty(self):
        """ Check if returns None if empty """
        session = queries.ErrorHandling().try_get_user_progress(user=None, tournament=None)
        self.assertEqual(session, None)

    def test_try_get_user_progress_user(self):
        """ Check if returns None if only given a user """
        session = queries.ErrorHandling().try_get_user_progress(user=self.user, tournament=None)
        self.assertEqual(session, None)

    def test_try_get_user_progress(self):
        """ Check if returns None if only given a user """
        session = queries.ErrorHandling().try_get_user_progress(user=None, tournament=self.tournament)
        self.assertEqual(session, None)

    def test_try_get_user_progress_tournament(self):
        """ Check if returns progress given the data """
        user_login = CreatCommonInstances().login_as_common_user(self)
        self.client.get(self.tournament.get_absolute_url())
        session = queries.ErrorHandling().try_get_user_progress(user=user_login, tournament=self.tournament)
        self.assertIsNotNone(session)

    def test_tournament_exists_emtpy(self):
        """ Test if non-created tournament return none """
        tournament = queries.ErrorHandling().tournament_exists(slug="12341234abcdabcd")
        self.assertIsNone(tournament)

    def test_utournament_exists_slug(self):
        """ Test if created tournament returnes tournament """
        tournament = queries.ErrorHandling().tournament_exists(slug="math-quiz-1")
        self.assertIsNotNone(tournament)