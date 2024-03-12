import logging

from django.http.request import HttpRequest

from ..models import Pessoa


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


def get_pessoa(cpf: str) -> Pessoa | None:
    """Obtém uma pessoa a partir do CPF"""
    return Pessoa.objects.filter(pk=str(cpf)).first()
