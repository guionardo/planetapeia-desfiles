from django.contrib import messages
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from ..views.utils import NavBar, get_post_data


class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = "perfil.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not (pessoa := NavBar.get_pessoa(request)):
            messages.error(request, "Não foi possível identificar a pessoa logada")
            return redirect("home")

        context = {
            "pessoa": pessoa,
            "navbar": {"links": [{"label": "Home", "link": reverse("home")}]},
        }
        return self.render_to_response(context)


class PerfilAlterarSenhaView(LoginRequiredMixin, TemplateView):
    template_name = "perfil_alterar_senha.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        nome_pessoa = request.user.get_full_name() or "não informado"
        label_nome = "Usuário administrador"
        if pessoa := NavBar.get_pessoa(request):
            nome_pessoa = pessoa.nome
            label_nome = "CPF"
        context = dict(
            header="Alteração de senha",
            label_nome=label_nome,
            username=request.user.get_username(),
            fullname=nome_pessoa,
            navbar=NavBar(request),
        )

        return self.render_to_response(context)

    def post(self, request: HttpRequest):
        senha_atual, senha_1, senha_2 = get_post_data(
            request, "senha_atual", "senha_1", "senha_2"
        )

        try:
            if not senha_atual:
                raise ValidationError("Senha atual não foi informada")
            if not senha_1 or senha_1 != senha_2:
                raise ValidationError("Verifique a nova senha e sua confirmação")
            if senha_atual == senha_1:
                raise ValidationError("Nova senha é idêntica à anterior")
            if not (
                user := authenticate(
                    username=request.user.username, password=senha_atual
                )
            ):
                raise ValidationError("Senha atual não está correta")
            password_validation.validate_password(senha_1)

            user.set_password(senha_1)
            messages.success(request, "Senha alterada com sucesso!")
            return redirect("perfil")

        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

        return redirect("perfil_senha")
