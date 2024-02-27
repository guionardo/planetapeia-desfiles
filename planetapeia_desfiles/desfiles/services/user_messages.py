import logging

from django.contrib.auth.models import AnonymousUser, User
from django.http.request import HttpRequest

from ..models import Pessoa, UserMessage, UserMessageLevelChoices
from ..models_utils import get_robot_user


class UserMessages:
    def __init__(self, request: HttpRequest):
        self.user = (
            get_robot_user()
            if isinstance(request.user, AnonymousUser)
            else request.user
        )
        self.log = logging.getLogger(self.__class__.__name__)

    def get_unreadmessages(self):
        if self.user.is_active:
            return list(
                UserMessage.objects.filter(user_to=self.user, read_at=None).order_by(
                    "when"
                )
            )
        return []

    def send_message(
        self,
        user_to: User | Pessoa,
        message: str,
        level: UserMessageLevelChoices = UserMessageLevelChoices.INFO,
    ):
        try:
            if isinstance(user_to, Pessoa):
                user_to = user_to.get_user()
            msg = UserMessage.objects.create(
                user_from=self.user, user_to=user_to, message=message, level=level
            )
            self.log.info(f"{msg}")
        except Exception as exc:
            self.log.error(
                f"Erro ao enviar mensagem {self.user} -> {user_to} : {level} : {message} - {exc}"
            )
