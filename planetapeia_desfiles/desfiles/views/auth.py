from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from . import get_post_data
from .utils.navbar import NavBar


class LoginView(TemplateView):
    template_name = "login.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = {
            "navbar": NavBar(request),
            "header": "Login",
        }

        return self.render_to_response(context)

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        cpf, senha = get_post_data(request, "cpf", "senha")
        if user := authenticate(request, username=cpf, password=senha):
            login(request, user)
            return HttpResponseRedirect(reverse("home"))


@login_required
def logoff(request: HttpRequest) -> HttpResponse:
    if request.user:
        messages.info(
            request,
            f"Logoff do usuário {request.user.get_full_name() or request.user.get_username()}",
        )
        logout(request)
    return redirect("index")
