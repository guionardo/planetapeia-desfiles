import logging

from django.contrib.auth.models import User
from django.http.request import HttpRequest

from ..models import Pessoa, UserMessage, UserMessageLevelChoices, PessoaRevisarSenha
from ..models_utils import get_robot_user


class UserMessages:
    def __init__(self, request: HttpRequest):
        self.user = request.user
        self.log = logging.getLogger(self.__class__.__name__)

    def get_unreadmessages(self):
        if self.user.is_active:
            for msg in UserMessage.objects.filter(
                user_to=self.user, read_at=None
            ).order_by("when"):
                yield msg
            for msg in self.get_revisoes_senha():
                yield msg

    def get_revisoes_senha(self):
        if self.user.is_active and self.user.is_staff:
            if count := PessoaRevisarSenha.objects.filter(
                ativa=True, atendida_por=None
            ).count():
                yield UserMessage(
                    user_from=get_robot_user(),
                    user_to=self.user,
                    message=f"Revisão de senha de usuários: {count}",
                    level=UserMessageLevelChoices.WARN,
                    link=None,
                )  # TODO: Implementar view para visualização de revisão de senha de usuários

    def send_message(
        self,
        user_to: User | Pessoa,
        message: str,
        level: UserMessageLevelChoices = UserMessageLevelChoices.INFO,
        link: str | None = None,
    ):
        try:
            user_from = get_robot_user() if not self.user.is_active else self.user
            if isinstance(user_to, Pessoa):
                user_to = user_to.get_user()
            msg = UserMessage.objects.create(
                user_from=user_from,
                user_to=user_to,
                message=message,
                level=level,
                link=link,
            )
            self.log.info(f"{msg}")
        except Exception as exc:
            self.log.error(
                f"Erro ao enviar mensagem {self.user} -> {user_to} : {level} : {message} - {exc}"
            )
