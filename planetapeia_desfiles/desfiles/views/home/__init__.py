from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.views.generic import TemplateView

from ..utils import NavBar
from .convites_ativos import get_convites_ativos
from .convites_pendentes import get_convites_pendentes
from .desfiles_ativos import get_desfiles_ativos
from .meus_convites import get_meus_convites
from .revisoes_senha import get_revisoes_senha
from .trajes import get_trajes


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home/home.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = {
            "navbar": NavBar(request),
            "header": "Home",
            "cards": [
                get_convites_pendentes(request),
                get_convites_ativos(request),
                get_desfiles_ativos(request),
                get_revisoes_senha(request),
                get_meus_convites(request),
                get_trajes(request),
            ],
        }
        return self.render_to_response(context)


paths = [path("home", HomeView.as_view(), name="home")]
