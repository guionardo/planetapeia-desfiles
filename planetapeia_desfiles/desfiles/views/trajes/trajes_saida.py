from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.views.generic import TemplateView

from ...roles import ALMOXARIFE
from ..utils import NavBar, get_post_data


class TrajesSaida(LoginRequiredMixin, TemplateView):
    template_name = "trajes/saida.html"

    def get(self, request: HttpRequest, num_inventario: int) -> HttpResponse:
        if not request.user.has_perm(ALMOXARIFE):
            return HttpResponseForbidden()
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }

        return self.render_to_response(context)

    def post(self, request: HttpRequest, num_inventario: int) -> HttpResponse:
        cpf, inventario = get_post_data(request, "cpf", "inventario")
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }

        return self.render_to_response(context)
