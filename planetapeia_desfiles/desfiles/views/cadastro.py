from typing import Any

from django.contrib import messages
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ..models import Grupo, Pessoa
from .redirect_crypt import HttpEncryptedRedirectResponse
from .utils.navbar import NavBar


class CadastroPessoaView(TemplateView):
    template_name = "cadastro_pessoa.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        query = HttpEncryptedRedirectResponse.get_data(request) or {}
        cpf = query.get("cpf")
        convite_hash = query.get("convite")
        if grupo_id := query.get("grupo"):
            grupo = str(Grupo.objects.get(pk=grupo_id))
        else:
            grupo = "Grupo não foi definido para este convite"

        context = {
            "cpf": cpf,
            "navbar": NavBar(request),
            "header": "Cadastro de Pessoa",
            "grupo": grupo,
            "grupo_id": grupo_id,
            "convite": convite_hash,
        }
        return self.render_to_response(context)

    def post(self, request: HttpRequest) -> HttpResponse:
        context = {}
        try:
            data = dict(
                cpf=request.POST.get("cpf"),
                nome=request.POST.get("nome"),
                telefone=request.POST.get("telefone"),
                data_nascimento=request.POST.get("data_nascimento"),
                genero=request.POST.get("genero"),
                peso=int(request.POST.get("peso", 0)),
                altura=int(request.POST.get("altura", 0)),
                tamanho_traje=request.POST.get("tamanho_traje"),
                pcd=bool(request.POST.get("pcd")),
                grupo_id=int(request.POST.get("grupo_id")),
                foto=request.FILES.get("foto"),
            )
            pessoa: Pessoa = Pessoa.objects.create(**data)
            if pessoa.created_password:
                messages.success(
                    request,
                    f"{pessoa.nome} foi registrada com o login {pessoa.cpf} e senha {pessoa.created_password}. Guarde essa informação.",
                )

            return redirect("login")

        except Exception as exc:
            print(exc)

        return self.render_to_response(context)
