from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from ...views.utils import NavBar


class FotoView(LoginRequiredMixin, TemplateView):
    template_name = "perfil/perfil_foto.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if disabled := not request.pessoa:
            messages.warning(
                request,
                f"O usuário {request.user} é um administrador sem perfil de pessoa. Não há fotografia vinculada a ele",
            )
        context = dict(navbar=NavBar(request), foto=request.foto, disabled=disabled)

        return self.render_to_response(context)

    def post(self, request: HttpRequest):
        return self.render_to_response({})
