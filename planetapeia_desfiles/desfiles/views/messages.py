from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ..views.utils import NavBar


class MessagesView(LoginRequiredMixin, TemplateView):
    template_name = "perfil_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not (pessoa := request.pessoa):
            messages.error(request, "Não foi possível identificar a pessoa logada")
            return redirect("home")

        context = {
            "pessoa": pessoa,
            "navbar": NavBar(request),
            "header": "Perfil",
            "readonly": True,
        }
        return self.render_to_response(context)
