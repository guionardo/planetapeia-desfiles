from dataclasses import dataclass, field
import json
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView
from django.contrib import messages
from ... import roles
from ..utils import NavBar
from ...models_utils import get_pessoa_name

# Obter as permissões atuais
roles_desc = []
roles_names = sorted(roles.roles.keys())
roles_desc = [roles.roles[role][0] for role in roles_names]
user_content_type = ContentType.objects.filter(app_label="auth", model="user").first()


@dataclass
class UserRoles:
    pk: int
    user_name: str
    is_active: bool
    is_superuser: bool
    roles: list[bool] = field(default_factory=list)

    def __lt__(self, other):
        return self.user_name < other.user_name


class RolesView(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "admin/roles.html"
    permission_required = roles.ADM_PESSOAS

    @classmethod
    def get_users(cls):
        users = []
        for user in get_user_model().objects.filter(is_staff=True):
            # Permissões do usuário
            permissions = set(
                p.codename
                for p in Permission.objects.filter(Q(user=user) | Q(group__user=user))
            )

            user_roles = UserRoles(
                pk=user.pk,
                user_name=get_pessoa_name(user),
                is_superuser=user.is_superuser,
                is_active=user.is_active,
                roles=[
                    True if user.is_superuser else role in permissions
                    for role in roles_names
                ],
            )

            users.append(user_roles)
        return sorted(users)

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "navbar": NavBar(request),
            "header": "Gestão de pessoas",
            "roles": roles.roles,
            "roles_desc": roles_desc,
            "users": self.get_users(),
        }

        return self.render_to_response(context)

    def post(self, request: HttpRequest) -> HttpResponse:
        for user in get_user_model().objects.filter(is_staff=True):
            is_active = bool(request.POST.get(f"{user.pk}_is_active"))
            user_roles = {
                name: bool(request.POST.get(f"{user.pk}_{index}"))
                for index, name in enumerate(roles_names, 1)
            }
            if is_active != user.is_active:
                if request.user == user:
                    messages.warning(
                        request, "Não é possível desativar o próprio usuário"
                    )
                    continue
                messages.info(
                    request,
                    f"Usuário {user}: {'reativado' if is_active else 'desativado'}",
                )

                user.is_active = is_active
                user.save()
                change = dict(active=is_active)
                LogEntry.objects.create(
                    user=request.user,
                    content_type=user_content_type,
                    object_id=user.pk,
                    object_repr=repr(user),
                    action_flag=CHANGE,
                    change_message=json.dumps(change),
                )

            username = get_pessoa_name(user)
            if user.is_superuser:
                continue  # Não é necessário atribuir permissões aos super usuários

            for role, enabled in user_roles.items():
                permission = user.user_permissions.filter(codename=role).first()
                rolename = roles_desc[roles_names.index(role)]
                change = dict(permission=role, permission_name=rolename)
                if permission and not enabled:
                    messages.info(
                        request, f"Removida permissão {rolename} do usuário {username}"
                    )
                    user.user_permissions.remove(permission)
                    change["action"] = "add"

                elif enabled and not permission:
                    if user.is_superuser:
                        break
                    messages.info(
                        request,
                        f"Adicionada permissão {rolename} ao usuário {username}",
                    )
                    permission = Permission.objects.filter(codename=role).first()
                    user.user_permissions.add(permission)
                    change["action"] = "remove"

                if change.get("action"):
                    LogEntry.objects.create(
                        user=request.user,
                        content_type=user_content_type,
                        object_id=user.pk,
                        object_repr=repr(user),
                        action_flag=CHANGE,
                        change_message=json.dumps(change),
                    )

        context = {
            "navbar": NavBar(request),
            "header": "Gestão de pessoas",
            "roles": roles.roles,
            "roles_desc": roles_desc,
            "users": self.get_users(),
        }
        return self.render_to_response(context)
