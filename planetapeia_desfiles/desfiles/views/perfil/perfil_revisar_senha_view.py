from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...models_utils import cpf_validator
from ...services import auth_service
from ..utils import NavBar


class RevisarSenha(TemplateView):
    template_name = "perfil/perfil_revisar_senha.html"

    def get(self, request: HttpRequest, cpf: str) -> HttpResponse:
        if auth_service.ha_revisao_ativa(request, cpf):
            return redirect("login")
        try:
            cpf_validator(cpf)
        except ValidationError:
            messages.warning(request, "CPF inválido")
            return redirect("login")

        context = dict(header="Revisar senha", navbar=NavBar(request), cpf=cpf)
        return self.render_to_response(context)

    def post(self, request: HttpRequest, cpf):
        if revisao := auth_service.criar_revisao_senha(cpf):
            if User.objects.filter(is_active=True, is_staff=True).count():
                messages.success(
                    request, "Notificação enviada aos usuários administradores"
                )
            else:
                messages.error(request, "Não há usuário administrador disponível")
            response = redirect("login")
            response.set_cookie("PD_PR", revisao.pk, httponly=True)
        else:
            messages.error(
                request, f"Não foi possível criar revisão de senha para o CPF {cpf}"
            )
            response = redirect("login")

        return response
