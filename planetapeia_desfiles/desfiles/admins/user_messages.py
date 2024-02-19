import datetime
from collections.abc import Sequence
from typing import Any

from django.contrib import admin
from django.contrib.admin.filters import RelatedFieldListFilter
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http import HttpRequest

from ..models import UserMessage
from ..services.mem_cache import MemCache


class PessoasCache:
    def __init__(self):
        self.cache = MemCache()

    def get_nome(self, username: str) -> str:
        if not (nome := self.cache.get(username)):
            user = User.objects.get(username=username)
            nome = user.get_full_name() or user.get_username()
            self.cache.set(username, nome)
        return nome


pessoas_cache = PessoasCache()


@admin.action(description="Marcar como lidas")
def marcar_como_lidas(modeladmin, request, queryset):
    queryset.update(read_at=datetime.datetime.now())


class PessoaFilter(RelatedFieldListFilter):
    def choices(self, changelist):
        for i, choice in enumerate(super().choices(changelist)):
            if i > 0:
                pessoa = pessoas_cache.get_nome(choice["display"])
                choice["display"] = pessoa
            yield choice


class UserMessagesAdmin(admin.ModelAdmin):
    # fields = ("level", "get_transito", "title", "message")
    read_only_fields = ["when", "level", "get_transito", "title", "message"]
    actions = [marcar_como_lidas]
    list_filter = ["level", ("user_from", PessoaFilter), ("user_to", PessoaFilter)]

    def get_list_display(self, request: HttpRequest) -> Sequence[str]:
        list_display = ["when", "level", "get_remetente"]
        if not request.pessoa:
            list_display.append("get_destinatario")
        list_display.extend(["title", "message", "read_at"])
        return list_display

    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
        list_filter = [
            "level",
            ("user_from", PessoaFilter),
        ]
        if not request.pessoa:
            list_filter.append(("user_to", PessoaFilter))
        return list_filter

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        if request.pessoa:
            return UserMessage.objects.filter(user_to=request.user)
        return super().get_queryset(request)

    @admin.display(description="Remetente")
    def get_remetente(self, obj):
        return pessoas_cache.get_nome(obj.user_from.username)

    @admin.display(description="Destinatário")
    def get_destinatario(self, obj):
        return pessoas_cache.get_nome(obj.user_to.username)

    @admin.display(description="Trânsito")
    def get_transito(self, obj):
        return f"{pessoas_cache.get_nome(obj.user_from.username)} -> {pessoas_cache.get_nome(obj.user_to.username)}"
