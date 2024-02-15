"""
View para a página /
"""


from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView


from .utils import NavBar


class Index(TemplateView):
    template_name = "index.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = {
            "header": "Sistema de gestão de desfiles",
            "navbar": NavBar(request),
        }
        if request.user.is_authenticated:
            context["user"] = str(request.user)

        return self.render_to_response(context)
