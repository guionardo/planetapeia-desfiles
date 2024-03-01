from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from ...services.user_messages import UserMessages
from ...views.utils import NavBar, use_plural


class MensagensView(LoginRequiredMixin, TemplateView):
    template_name = "perfil/mensagens.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"navbar": NavBar(request)}
        return self.render_to_response(context)

    def post(self, request: HttpRequest):
        navbar = NavBar(request)
        readen_msg = {
            msg.pk: bool(request.POST.get(f"msg_{msg.pk}"))
            for msg in navbar.user_messages
            if msg.pk
        }
        updated_count = 0
        for pk, readen in readen_msg.items():
            if UserMessages.set_readen(pk, readen):
                updated_count += 1
        messages.info(
            request,
            f"{updated_count} {use_plural(updated_count,'mensagem atualizada','mensagens atualizadas')}",
        )

        context = {"navbar": NavBar(request)}
        return self.render_to_response(context)
