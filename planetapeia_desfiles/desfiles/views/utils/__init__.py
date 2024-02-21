__all__ = ["NavBar"]
from django.http.request import HttpRequest

from .navbar import NavBar


def get_post_data(request: HttpRequest, *variables, default_empty=""):
    return (request.POST.get(var, default_empty) for var in variables)
