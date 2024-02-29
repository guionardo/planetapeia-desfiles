from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from ...models import Pessoa
from ..utils import NavBar, get_post_data, use_genero


class LoginView(TemplateView):
    template_name = "auth/login.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_active:
            messages.info(request, "Você já está conectado ao sistema")
            return redirect("home")

        context = {
            "navbar": NavBar(request),
            "header": "Login",
        }

        return self.render_to_response(context)

    def post(self, request: HttpRequest) -> HttpResponse:
        cpf, senha = get_post_data(request, "cpf", "senha")

        if not (user := authenticate(request, username=cpf, password=senha)):
            context = {
                "navbar": NavBar(request),
                "header": "Login",
            }
            # Verificar se seu usuário existe
            if pessoa := Pessoa.objects.filter(pk=cpf).first():
                messages.error(request, "Credenciais inválidas!")
                messages.warning(
                    request,
                    "Se você está tendo problemas com sua senha, clique em 'Solicitar nova senha'."
                    " Um administrador fará a revisão das suas credenciais.",
                )
                context.update({"revisar_senha": True, "cpf": cpf})

            return self.render_to_response(context)

        if pessoa := Pessoa.objects.filter(pk=user.username).first():
            login_greet = use_genero(request, "Bem vind") + " " + pessoa.nome
        else:
            login_greet = f"Bem vindo {user.get_fullname() or user.get_username()}"
        if user.last_login:
            login_greet += (
                f" - seu último acesso foi em {user.last_login:%d/%m/%Y %H:%M}"
            )
        login(request, user)
        messages.info(request, login_greet)
        return HttpResponseRedirect(reverse("home"))
