from django.http import HttpResponseRedirect
from django.urls import reverse
from . import queries

""" Wrapper for caching users information """
def cache_user_information():
    def _method_wrapper(f):
        def _arguments_wrapper(request, *args, **kwargs):
            # Get the tournament the user is on, if any
            tournament = queries.ErrorHandling().tournament_exists(kwargs.get('slug'))
            # Create the singleton instance, this is created each page call for the given page due to erros
            queries.UserSessionCache().getInstance().setUp(user=request.user, tournament=tournament, request=request)
            return f(request, *args, **kwargs)
        return _arguments_wrapper
    return _method_wrapper

""" Wrapper for redrecting to different pages """
def redirect_on_post_get(get, post):
    def _method_wrapper(f):
        def _arguments_wrapper(request, *args, **kwargs):
            if request.method == 'GET':
                return HttpResponseRedirect(reverse(get))
            else:
                return HttpResponseRedirect(reverse(post))

            return f(request, *args, **kwargs)
        return _arguments_wrapper
    return _method_wrapper

""" Checks if a user is a admin, if not rasies a error """
def is_admin(f):
    def wrapper(*args, **kwargs):
        # Check if user is a staff member
        if (args[0].user.is_staff):
            # Returns if so
            return f(*args, **kwargs)
        # Else rasie error
        return PermissionError
    return wrapper