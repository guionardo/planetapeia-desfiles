import datetime
import logging

from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.urls import reverse

from ..models import Pessoa, PessoaRevisarSenha, UserMessage, UserMessageLevelChoices
from ..models_utils import get_robot_user
from ..services.date_time_provider import DateTimeProvider


class UserMessages:
    def __init__(self, request: HttpRequest):
        self.user = request.user
        self.log = logging.getLogger(self.__class__.__name__)

    def get_messages(self):
        if self.user.is_active:
            for msg in UserMessage.objects.filter(user_to=self.user).order_by("when"):
                yield msg
            for msg in self.get_revisoes_senha():
                yield msg

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
            for revisao in PessoaRevisarSenha.objects.filter(
                ativa=True, atendida_por=None
            ).order_by("data_solicitacao"):
                yield UserMessage(
                    user_from=get_robot_user(),
                    user_to=self.user,
                    when=revisao.data_solicitacao,
                    title="Revisão de senha",
                    message=str(revisao.pessoa),
                    link=reverse("admin:desfiles_pessoarevisarsenha_changelist")
                    + "?atendida_por__isempty=1",
                )

    def messages_count(self) -> dict:
        """Retorna o número de mensagens do usuário
        {"readen":0, "unreaden":0}
        """
        count = {"readen": 0, "unreaden": 0}
        if self.user.is_active:
            count["readen"] = UserMessage.objects.filter(
                user_to=self.user, read_at__gt=datetime(2000, 1, 1)
            ).count()
            count["unreaden"] = UserMessage.objects.filter(
                user_to=self.user, read_at=None
            ).count()

        return count

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

    @classmethod
    def set_readen(cls, message_id, is_readen: bool) -> bool:
        if message := UserMessage.objects.filter(pk=message_id).first():
            if bool(message.read_at) != bool(is_readen):
                message.read_at = DateTimeProvider.now() if is_readen else None
                message.save(update_fields=["read_at"])
                return True
