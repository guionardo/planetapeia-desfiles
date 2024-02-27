from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest

from ..models import Pessoa, PessoaRevisarSenha
from ..models_utils import default_user_password


def atualizar_senha_revisada(revisao: PessoaRevisarSenha, request: HttpRequest) -> bool:
    """Atualiza senha do usuário caso a revisão tenha sido atendida por um administrador
    Retorna True em caso de atualização com sucesso"""
    nova_senha = default_user_password(
        revisao.pessoa.cpf, revisao.pessoa.nome, revisao.pessoa.data_nascimento
    )
    if revisao.atendida_por:
        revisao.pessoa.get_user().set_password(nova_senha)
        revisao.ativa = False
        revisao.save()
        messages.success(
            request,
            f"Sua senha foi redefinida automaticamente para {nova_senha} pelo usuário {revisao.atendida_por} em {revisao.atendida_em:%d/%m/%Y %H:%M}",
        )
        if isinstance(request.user, AnonymousUser):
            login(request, revisao.pessoa.get_user())
            messages.info(
                request, f"Já efetuei o login automático do usuário {revisao.pessoa}"
            )
        return True
    else:
        messages.warning(
            request,
            "Os usuários administradores já foram notificados, mas ainda não há uma revisão disponível para seu acesso",
        )


def get_revisao(guid: str) -> PessoaRevisarSenha:
    return PessoaRevisarSenha.objects.filter(pk=guid, ativa=True).first()


def ha_revisao_ativa(request: HttpRequest, cpf: str) -> bool:
    if not (pessoa := Pessoa.objects.filter(pk=cpf).first()):
        # Pessoa não encontrada
        messages.warning(request, "CPF não encontrado")
        return
    return PessoaRevisarSenha.objects.filter(pessoa=pessoa, ativa=True).first()


def criar_revisao_senha(cpf: str) -> PessoaRevisarSenha | None:
    if pessoa := Pessoa.objects.filter(pk=cpf).first():
        return PessoaRevisarSenha.objects.create(pessoa=pessoa)
