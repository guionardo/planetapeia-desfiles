import logging

from django.contrib.auth.models import User
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


class PessoaService:
    def __init__(self, request: HttpRequest):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.user: User | None = request.user if request.user.is_active else None
        self.pessoa: Pessoa | None = None

        try:
            self.pessoa = Pessoa.objects.get(pk=self.user.username)
        except Pessoa.DoesNotExist:
            self.logger.info("Pessoa não identificada para o user %s", self.user)
        finally:
            self.logger.info("REQUEST USER = %s | PESSOA = %s", self.user, self.pessoa)
