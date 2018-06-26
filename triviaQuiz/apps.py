from django.apps import AppConfig


class TriviaquizConfig(AppConfig):
    name = 'triviaQuiz'

    def ready(self):
        import triviaQuiz.signals