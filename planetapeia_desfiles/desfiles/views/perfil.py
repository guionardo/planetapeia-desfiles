from django.contrib import messages
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ..views.utils import NavBar, get_post_data


class PerfilView(LoginRequiredMixin, TemplateView):
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


class PerfilEditarView(LoginRequiredMixin, TemplateView):
    template_name = "perfil_form.html"

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


class PerfilAlterarSenhaView(LoginRequiredMixin, TemplateView):
    template_name = "perfil_alterar_senha.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        nome_pessoa = request.user.get_full_name() or "não informado"
        label_nome = "Usuário administrador"
        if pessoa := request.pessoa:
            nome_pessoa = pessoa.nome
            label_nome = "CPF"
        context = dict(
            header="Alteração de senha",
            label_nome=label_nome,
            username=request.user.get_username(),
            fullname=nome_pessoa,
            navbar=NavBar(request),
        )

        return self.render_to_response(context)

    def post(self, request: HttpRequest):
        senha_atual, senha_1, senha_2 = get_post_data(
            request, "senha_atual", "senha_1", "senha_2"
        )

        try:
            if not senha_atual:
                raise ValidationError("Senha atual não foi informada")
            if not senha_1 or senha_1 != senha_2:
                raise ValidationError("Verifique a nova senha e sua confirmação")
            if senha_atual == senha_1:
                raise ValidationError("Nova senha é idêntica à anterior")
            if not (
                user := authenticate(
                    username=request.user.username, password=senha_atual
                )
            ):
                raise ValidationError("Senha atual não está correta")
            password_validation.validate_password(senha_1)

            user.set_password(senha_1)
            messages.success(request, "Senha alterada com sucesso!")
            return redirect("perfil")

        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

        return redirect("perfil_senha")


class PerfilFotoView(LoginRequiredMixin, TemplateView):
    pass
