from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from triviaQuiz.models import Tournament, Question, QuestionAnswer, QuestionIncorrect, TournamentScore, UserProgress
from urllib.parse import unquote
from django.utils.text import slugify
from triviaQuiz.services import get_questions

@receiver(pre_save, sender=Tournament)
def created_tournament_slug(sender, **kwards):
    # Get the pre_created instance
    pre_created = kwards['instance']
    # Slugify the name
    slug = slugify(pre_created.name)
    # Check if there're any tournaments in the database
    if (Tournament.objects.all().count() == 0):
        # Since we increment the number later we use 0 since this database starts at 1.
        next_id = 0
    else:
        next_id = Tournament.objects.order_by('-pk')[0].id
    # Set the slug name for the tournament, given the slug and the id
    pre_created.slug = "%s-%d" % (slug, (next_id + 1))

@receiver(post_save, sender=Tournament)
def created_tournament(sender, **kwards):
    # Check if instance was created
    if (kwards['created']):
        # Get the created instance
        created = kwards['instance']
        # Get questions for the created instance
        questions = get_questions(created)
        # Check if the tournament has questions
        if (not questions):
            #created.delete()
            created.active = False
        else:
            # Create the questions
            create_questions(questions, created)

def create_questions(questions, tournament):
    for question in questions:
        # Create a question
        question_instance = Question.objects.create(question=unquote(question['question']), tournament=tournament)
        # Create a answer for the question
        QuestionAnswer.objects.create(option=unquote(question['correct_answer']), question=question_instance)
        # Create the incorrect answers
        for o in question['incorrect_answers']:
            QuestionIncorrect.objects.create(option=unquote(o), question=question_instance)
    return questions