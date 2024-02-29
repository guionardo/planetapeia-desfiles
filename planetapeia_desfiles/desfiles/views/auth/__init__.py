from django.urls import path

from .login_view import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


@login_required
def logoff(request: HttpRequest) -> HttpResponse:
    if request.user:
        messages.info(
            request,
            f"Logoff do usuário {request.user.get_full_name() or request.user.get_username()}",
        )
        logout(request)
    return redirect("index")


paths = [
    path("login", LoginView.as_view(), name="login"),
    path("logoff", logoff, name="logoff"),
]
