import logging

from django.http.request import HttpRequest

from ..models import Pessoa
from ..services.mem_cache import MemCache


def get_pessoa_from_request(request: HttpRequest) -> Pessoa | None:
    pessoa = None
    try:
        if request.user.is_active:
            pessoa = Pessoa.objects.get(pk=request.user.username)

    except Pessoa.DoesNotExist:
        logging.getLogger(__name__).info(
            "Pessoa não identificada para o user %s", request.user
        )
    finally:
        logging.getLogger(__name__).info(
            "REQUEST USER = %s | PESSOA = %s", request.user, pessoa
        )
    return pessoa


class PessoaMiddleware:
    """Injeção do objeto pessoa logada na requisição"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.pessoas = MemCache()

    def get_pessoa(self, request: HttpRequest):
        if not request.user.is_active:
            return None
        if pessoa := self.pessoas.get(request.user.pk):
            return pessoa
        pessoa = get_pessoa_from_request(request)
        self.pessoas.set(request.user.pk, pessoa)
        return pessoa

    def __call__(self, request: HttpRequest):
        request.pessoa = self.get_pessoa(request)
        response = self.get_response(request)

        return response
