from datetime import date

from django.contrib import messages
from django.forms import ValidationError
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from ...models import (
    AprovacaoChoices,
    Convite,
    Desfile,
    InscricaoDesfile,
    Pessoa,
    TiposPessoasChoices,
    StaffPadrao,
)
from ...models_utils import cpf_validator
from ..utils import HttpEncryptedRedirectResponse, NavBar


class ConviteView(TemplateView):
    template_name = "convite/convite.html"

    def _get_convite(self, hash: str) -> Convite:
        if convite := Convite.objects.filter(hash=hash).first():
            if convite.valido_ate < date.today():
                raise ValidationError(
                    f"Este convite não é mais válido ({convite.valido_ate:%d/%m/%Y})"
                )
            if convite.convidados_confirmados >= convite.max_convidados:
                raise ValidationError(
                    f"O limite de {convite.max_convidados} pessoas para este convite já foi atingido"
                )
            return convite
        else:
            raise Convite.DoesNotExist()

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        hash = kwargs.get("hash")
        convite = None
        context = {
            "navbar": NavBar(request),
            "title": "Planetapéia - Convite",
            "header": "Convite inválido",
        }
        try:
            if not hash:
                messages.error(
                    request,
                    "Você deve utilizar o link de convite fornecido pelo seu padrinho ou líder de grupo",
                )
            else:
                convite = self._get_convite(hash)
                context.update(
                    {
                        "convite": convite,
                        "desfile": convite.desfile,
                        "header": f"Convite para o desfile {Desfile.objects.first()}",
                        "cpf": request.user.username,
                    }
                )

        except Convite.DoesNotExist:
            messages.error(request, "Convite não foi encontrado")

        except ValidationError as exc:
            for message in exc.messages:
                messages.error(request, message)

        except Exception as exc:
            messages.error(request, str(exc))

        return self.render_to_response(context=context)

    def post(self, request: HttpRequest, hash: str) -> HttpResponse:
        pessoa = None
        desfile = None
        inscricao = None
        try:
            convite = self._get_convite(hash)
            desfile = convite.desfile
            cpf = request.POST.get("cpf")
            cpf_validator(cpf)
            pessoa = Pessoa.objects.get(pk=cpf)

            if inscricao := InscricaoDesfile.objects.filter(
                desfile=convite.desfile, pessoa=pessoa
            ).first():
                if inscricao.aprovacao == AprovacaoChoices.REJEITADO:
                    messages.warning(
                        request,
                        f"Verifique a inscrição de {pessoa} junto com seu padrinho ou responsável pelo grupo",
                    )
                else:
                    messages.warning(request, f"Inscrição: {inscricao}")
                return redirect("login")
            else:
                tipo_pessoa = TiposPessoasChoices.CONVIDADO
                veiculo = None
                if staff_padrao := StaffPadrao.objects.filter(pessoa=pessoa).first():
                    # TODO: Implementar verificação nos staff-padrão para obter o tipo
                    veiculo = staff_padrao.staff_padrao_veiculo.veiculo
                    tipo_pessoa = pessoa.tipo

                inscricao = InscricaoDesfile.objects.create(
                    desfile=desfile,
                    pessoa=pessoa,
                    tipo_pessoa=tipo_pessoa,
                    convite=convite,
                    veiculo=veiculo,
                )
                messages.success(request, f"Inscrição {inscricao}")

        except Convite.DoesNotExist:
            messages.error(request, "Convite não foi encontrado")

        except Pessoa.DoesNotExist:
            response = HttpEncryptedRedirectResponse(
                reverse("cadastro_pessoa"),
                data={"cpf": cpf, "grupo": convite.grupo.id, "convite": hash},
                use_query=True,
            )
            return response

        except Exception as exc:
            messages.error(request, str(exc))

        return self.render_to_response(
            context={
                "title": "Planetapéia - Convite",
                "header": str(desfile),
                "navbar": NavBar(request),
                "convite": convite,
                "desfile": desfile,
                "pessoa": pessoa,
                "inscricao": inscricao,
            },
        )
