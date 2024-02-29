from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...views.utils import NavBar, get_post_data


class EditarView(LoginRequiredMixin, TemplateView):
    template_name = "perfil/perfil_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not (pessoa := request.pessoa):
            messages.error(request, "Não foi possível identificar a pessoa logada")
            return redirect("home")

        context = {
            "pessoa": pessoa,
            "navbar": NavBar(request),
            "header": "Perfil",
        }
        return self.render_to_response(context)

    def post(self, request: HttpRequest):
        (
            nome,
            telefone,
            data_nascimento,
            genero,
            peso,
            altura,
            tamanho_traje,
            pcd,
        ) = get_post_data(
            request,
            "nome",
            "telefone",
            "data_nascimento",
            "genero",
            "peso",
            "altura",
            "tamanho_traje",
            "pcd",
        )

        if not (pessoa := request.pessoa):
            messages.error(request, "Pessoa não foi identificada!")
            return redirect("home")

        pessoa.nome = nome
        pessoa.telefone = telefone
        pessoa.data_nascimento = data_nascimento
        pessoa.genero = genero
        pessoa.peso = int(peso)
        pessoa.altura = int(altura)
        pessoa.tamanho_traje = tamanho_traje
        pessoa.pcd = bool(pcd)

        if foto := request.FILES.get("foto"):
            pessoa.foto = foto

        pessoa.save()
        messages.success(request, "Dados atualizados")
        return redirect("perfil")
