from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from .utils import NavBar


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = {"navbar": NavBar(request)}
        return self.render_to_response(context)
        return super().get(request, *args, **kwargs)
