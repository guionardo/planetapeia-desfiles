from django.http.request import HttpRequest
from django.shortcuts import redirect

from ..services import auth_service


class PasswordRecoveryMiddleware:
    """Injeção do objeto pessoa logada na requisição"""

    def __init__(self, get_response):
        self.get_response = get_response

    def do_recovery(self, request: HttpRequest, guid: str) -> bool:
        """Efetuar a recuperação da senha do usuário, informando a nova senha"""
        if revisao := auth_service.get_revisao(guid):
            return auth_service.atualizar_senha_revisada(revisao, request)

    def __call__(self, request: HttpRequest):
        limpar_cookie = False
        if guid := request.COOKIES.get("PD_PR"):
            limpar_cookie = self.do_recovery(request, guid)

        if limpar_cookie:
            response = redirect("home")
            response.delete_cookie("PD_PR")
        else:
            response = self.get_response(request)

        return response
