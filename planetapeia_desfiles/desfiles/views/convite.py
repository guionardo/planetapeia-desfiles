from datetime import date

from django.forms import ValidationError
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from ..models import Convite, Desfile, Pessoa
from ..models_utils import cpf_validator
from ..navbar import NavBar
from . import encrypt_dict
from .redirect_crypt import HttpEncryptedRedirectResponse


class ConviteView(TemplateView):
    template_name = "convite.html"

    def _get_convite(self, hash: str) -> Convite:
        if convite := Convite.objects.filter(hash=hash).first():
            if convite.valido_ate < date.today():
                raise ValidationError("Este convite não é mais válido")
            if convite.convidados_confirmados >= convite.max_convidados:
                raise ValidationError(
                    f"O limite de {convite.max_convidados} pessoas para este convite já foi atingido"
                )
            return convite
        else:
            raise Convite.DoesNotExist()

    def get(self, request: HttpRequest, hash: str) -> HttpResponse:
        erro = None
        convite = None
        try:
            convite = self._get_convite(hash)

        except Convite.DoesNotExist:
            erro = "Convite não foi encontrado"

        except Exception as exc:
            erro = exc.message
        return self.render_to_response(
            context={
                "title": "Planetapéia - Convite",
                "header": f"Convite para o desfile {Desfile.objects.first()}",
                "navbar": NavBar().to_html(),
                "convite": convite,
                "desfile": Desfile.objects.first(),
                "erro": erro,
            },
        )

    def post(self, request: HttpRequest, hash: str) -> HttpResponse:
        erro = None
        pessoa = None
        try:
            convite = self._get_convite(hash)
            cpf = request.POST.get("cpf")
            cpf_validator(cpf)
            pessoa = Pessoa.objects.get(pk=cpf)

        except Convite.DoesNotExist:
            erro = "Convite não foi encontrado"
        except Pessoa.DoesNotExist:
            erro = "Não existe pessoa com este CPF"
            response = HttpEncryptedRedirectResponse(
                reverse("cadastro_pessoa"),
                data={"cpf": cpf, "grupo": convite.grupo.id, "convite": hash},
                use_query=True,
            )

            return response
            # TODO: Redirecionar para o cadastro
        except Exception as exc:
            erro = str(exc)
        return self.render_to_response(
            context={
                "title": "Planetapéia - Convite",
                "header": f"Convite para o desfile {Desfile.objects.first()}",
                "navbar": NavBar().to_html(),
                "convite": convite,
                "desfile": Desfile.objects.first(),
                "erro": erro,
                "pessoa": pessoa,
            },
        )
