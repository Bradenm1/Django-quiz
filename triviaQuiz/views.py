from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.base import TemplateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views import generic, View
from django.utils.decorators import method_decorator
from triviaQuiz.models import Tournament
from django.shortcuts import render
from triviaQuiz.decorators import redirect_on_post_get, cache_user_information
from . import queries
from . import forms
import datetime
 
# Create your views here.
@method_decorator(login_required, name='dispatch')
class IndexView(generic.TemplateView):
    """ View which allow users to acces the home page """

    template_name = "home.html"
    context_object_name = "active_tournaments_session"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        # Get the curretn user
        user = self.request.user
        completedTournaments = queries.CompletedTournaments(list(), user).get_infomration()
        # Get all greater then today
        future_tournaments = Tournament.customManager.future().all()
        # Get all missed tournaments given what the user has already completed
        missed_tournaments = queries.MissedTournaments(Tournament.customManager.missed().all(), user).get_infomration()
        # Get total missed tournaments as a count
        missed_tournaments_count = missed_tournaments.count()
        # Get all less then today
        active_tournaments_non_completed = queries.NonCompletedTournaments(Tournament.customManager.active().all(), user).get_infomration()
        # Get stats
        stats = queries.TournamentStats(user)
        # Get total correct questions overall
        total_correct = stats.getTotalCorrect()
        # Get number of tournaments participated in
        nTournamentsParticipated = stats.getNumberOfTournamentsParticipated()
        # Zip the two results to be used in the html, allows the progress bars to work
        active = zip(
                Tournament.customManager.progress(self.request.user), 
                active_tournaments_non_completed
            )
        context['active_tournaments_session'] = active
        context['active_tournaments'] = active_tournaments_non_completed
        context['future_tournaments'] = future_tournaments
        context['comepeted_tournaments'] = completedTournaments
        context['missed_tournaments'] = missed_tournaments
        context['total_correct'] = total_correct
        context['total_participated'] = nTournamentsParticipated
        context['total_missed'] = missed_tournaments_count
        # Check if the user is staff, if so show the in-active tournaments on the page
        if (user.is_staff):
            context['in_active'] = Tournament.objects.filter(active=False)
        return context
    
class SignUp(generic.CreateView):
    """ CreateView which allow users to register to the site """

    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@method_decorator(staff_member_required(login_url=reverse_lazy('login')), name='dispatch')
class CreateTournamentView(generic.CreateView):
    """ CreateView which allow creation of a tournament """

    form_class = forms.CreateTournamentForm
    model = Tournament
    template_name = 'tournament_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateTournamentView, self).get_context_data(**kwargs)
        # Get todays date to use in the html for the dateinputs
        context['minDate'] = datetime.datetime.today().strftime('%Y-%m-%d')
        return context

@method_decorator(login_required, name='dispatch')
class HighScoresView(generic.ListView):
    """ View which allow users to view highscores """

    template_name = "highscores.html"
    context_object_name = "high_scores"
    # pageinate for max number of high-scores per page
    paginate_by = 10

    def get_queryset(self, **kwards):
        highScores = Tournament.customManager.getHighScores()
        return highScores

@login_required
@cache_user_information()
def quiz(request, slug):
    # Check if tournament exists
    tournament = queries.ErrorHandling().tournament_exists(slug)
    # Check if it returned a result, if not it does not exist
    if (not tournament):
        context = {'message' : 'Tournament does not exist'}
        return render(request, 'message.html', context)
    else:
        # Check if tournament is not active and the user is not a admin
        if (not tournament.active and not request.user.is_staff):
            context = {'tournament' : tournament, 'message' : 'Tournament not active'}
            return render(request, 'message.html', context)
        else:
            # Check if tournament is empty
            if (tournament.isTournamentEmpty()):
                context = {'tournament' : tournament, 'message' : 'Tournament has no questions'}
                return render(request, 'tournament_no_questions.html', context)
    return queries.QuizTypeClient().run(request)

@method_decorator(staff_member_required(login_url=reverse_lazy('login')), name='dispatch')
class ShowTournamentQuestionsView(View):
    """ View which allow admin to view tournament questions """

    def post(self, request):
        # Get the tournament
        tournament = Tournament.objects.get(slug=request.POST['tournament_id'])
        # Get the questions for the tournament
        questions = Tournament.customManager.getCreationResult(tournament)
        context = {"questions" : questions,
                "tournament" : tournament
                }
        return context

class MessageAdminViews():

    def run(self, request):
        # Get the tournament slug
        tournament_slug = request.POST['tournament_id']
        # Get the tournament given the slug
        tournament = Tournament.objects.get(slug=tournament_slug)
        # run the body code for the other classes
        context = self.bodyCode(request, tournament)
        # Return the render result
        return render(request, 'message.html', context)

    def bodyCode(self, request, tournament):
        raise NotImplementedError()

class DeleteTournament(MessageAdminViews):

    def bodyCode(self, request, tournament):
        # Delete the tournament
        queries.AdminTools(request.user).deleteTournament(tournament=tournament)
        # The message to show the user
        context = { 'message' : 'Tournament Deleted' }
        # Add that to the context
        return context

class ActivateOrDeactivateTournament(MessageAdminViews):

    def bodyCode(self, request, tournament):
        # Check if the tournament is active
        if (tournament.active):
            tournament.active = False
            message = "Tournament has been deactivated"
        else:
            tournament.active = True
            message = "Tournament is now active"
        # Save the tournament result
        tournament.save()
        # Add that message to the context
        context = { 'message' : message }
        return context

class ResetSession(MessageAdminViews):

    def bodyCode(self, request, tournament):
        # Rest the score for the user given the tournament
        queries.AdminTools(request.user).resetScore(tournament=tournament, user=request.user)
        # Print what tournament was reset
        message = "Session and Score Reset:\n" + tournament.__str__()
        # Add that to the context
        context = { 'message' : message }
        return context

@method_decorator(staff_member_required(login_url=reverse_lazy('login')), name='dispatch')
class DeleteTournamentView(View):
    """ View which allow admins to delete tournaments """

    template_name = "message.html'"

    def post(self, request):
        context = DeleteTournament().run(request)
        return context

@method_decorator(staff_member_required(login_url=reverse_lazy('login')), name='dispatch')
class ActivateOrDeactivateTournamentView(View):
    """ View which allow admins to activate and deactive tournaments """

    template_name = "message.html'"

    def post(self, request):
        context = ActivateOrDeactivateTournament().run(request)
        return context      

@method_decorator(staff_member_required(login_url=reverse_lazy('login')), name='dispatch')
class ResetSessionView(View):
    """ View which alls admins to reset sessons and progress """

    template_name = "message.html'"

    def post(self, request):
        context = ResetSession().run(request)
        return context      