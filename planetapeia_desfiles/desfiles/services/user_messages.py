import logging

from django.contrib.auth.models import User
from django.http.request import HttpRequest

from ..models import UserMessage, UserMessageLevelChoices


class UserMessages:
    def __init__(self, request: HttpRequest):
        self.user = request.user
        self.log = logging.getLogger(self.__class__.__name__)

    def get_unreadmessages(self):
        return list(
            UserMessage.objects.filter(user_to=self.user, read_at=None).order_by("when")
        )

    def send_message(
        self,
        user_to: User,
        message: str,
        level: UserMessageLevelChoices = UserMessageLevelChoices.INFO,
    ):
        try:
            msg = UserMessage.objects.create(
                user_from=self.user, user_to=user_to, message=message, level=level
            )
            self.log.info(f"{msg}")
        except Exception as exc:
            self.log.error(
                f"Erro ao enviar mensagem {self.user} -> {user_to} : {level} : {message} - {exc}"
            )
