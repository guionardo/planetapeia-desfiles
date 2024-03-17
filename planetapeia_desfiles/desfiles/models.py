import datetime
import decimal
import logging
import os
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.urls import reverse

from . import roles
from .models_utils import (
    convite_hash,
    cpf_validator,
    data_nascimento_validator,
    default_user_password,
    get_robot_user,
    nome_pesquisavel,
    upload_to,
)
from .services.date_time_provider import DateTimeProvider
from .services.face_recognition import get_face_image


class GenerosChoices(models.TextChoices):
    MASCULINO = "M", "Masculino"
    FEMININO = "F", "Feminino"


class TamanhosTrajeChoices(models.TextChoices):
    P = "P", "Pequeno"
    M = "M", "Médio"
    G = "G", "Grande"
    GG = "E", "Extra-grande"


class TiposPessoasChoices(models.TextChoices):
    CONVIDADO = "C", "Convidado"
    STAFF = "S", "Staff"
    CONDUTOR = "D", "Condutor"


class TiposCobrancaTrajeChoices(models.TextChoices):
    GRUPO = "G", "Seguir grupo"
    SIM = "S", "Sim"
    NAO = "N", "Não"


class AprovacaoChoices(models.TextChoices):
    PENDENTE = "P", "Pendente"
    APROVADO = "A", "Aprovado"
    REJEITADO = "R", "Rejeitado"


class SituacaoTrajeChoices(models.TextChoices):
    DISPONIVEL = "D", "Disponível"
    EMPRESTADO = "E", "Emprestado"
    MANUTENCAO = "M", "Em Manutenção"
    DESCARTADO = "X", "Descartado"
    EXTRAVIADO = "x", "Extraviado"


class TrajeMovimentoChoices(models.TextChoices):
    ENTRADA = "E", "Entrada"
    EMPRESTIMO = "B", "Empréstimo"
    DEVOLUCAO = "D", "Devolução"
    MANUTENCAO = "M", "Manutenção"
    DESCARTE = "X", "Descarte"
    EXTRAVIO = "x", "Extravio"


class TrajeSituacaoTaxa(models.TextChoices):
    PENDENTE = "P", "Pendente"
    PAGO = "$", "Pago"
    ABONADO = "A", "Abonado"


class Pessoa(models.Model):
    is_cleaned = False
    created_password: str = ""

    cpf = models.CharField(
        verbose_name="CPF", primary_key=True, max_length=11, validators=[cpf_validator]
    )
    nome = models.CharField(
        verbose_name="Nome",
        max_length=60,
    )
    nome_busca = models.CharField(
        verbose_name="Nome busca", max_length=60, editable=False, blank=True, null=True
    )
    telefone = models.CharField(verbose_name="Telefone", max_length=13)
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento", validators=[data_nascimento_validator]
    )
    genero = models.CharField(
        verbose_name="Gênero", max_length=1, choices=GenerosChoices
    )
    peso = models.IntegerField(
        verbose_name="Peso (kg)",
        validators=[
            MinValueValidator(1, "Peso mínimo"),
            MaxValueValidator(160, "Peso máximo"),
        ],
    )
    altura = models.IntegerField(
        verbose_name="Altura (cm)",
        validators=[
            MinValueValidator(30, "Altura mínima 30"),
            MaxValueValidator(220, "Altura máxima 220"),
        ],
    )
    tamanho_traje = models.CharField(
        verbose_name="Tamanho do traje", max_length=1, choices=TamanhosTrajeChoices
    )
    pcd = models.BooleanField(verbose_name="Pessoa com deficiência", default=False)
    tipo = models.CharField(
        verbose_name="Tipo",
        max_length=1,
        choices=TiposPessoasChoices,
        default=TiposPessoasChoices.CONVIDADO,
    )
    tipo_cobranca_traje = models.CharField(
        verbose_name="Tipo cobrança traje",
        max_length=1,
        choices=TiposCobrancaTrajeChoices,
        default="G",
    )
    grupo = models.ForeignKey("Grupo", verbose_name="Grupo", on_delete=models.PROTECT)
    padrinho = models.ForeignKey(
        "Pessoa",
        verbose_name="Padrinho",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    foto = models.ImageField(
        verbose_name="Imagem",
        upload_to=upload_to,
        help_text="Logotipo para ser usada nos relatórios",
        null=True,
        blank=True,
    )

    def get_foto(self):
        if self.foto:
            foto_file = os.path.abspath(f'./{self.foto.url.removeprefix("/")}')
            url = get_face_image(foto_file)
            return static(os.path.basename(url))
        return static(
            "icon_male_black.svg"
            if self.genero == GenerosChoices.MASCULINO
            else "icon_female_black.svg"
        )

    @property
    def e_crianca(self) -> bool:
        return (datetime.date.today() - self.data_nascimento).days < (365.25 * 12)

    @property
    def cobrar_traje(self) -> bool:
        if self.tipo_cobranca_traje == TiposCobrancaTrajeChoices.GRUPO:
            return self.grupo.tipo_cobranca_traje
        return self.tipo_cobranca_traje == TiposCobrancaTrajeChoices.SIM

    def __str__(self):
        return self.nome

    def get_user(self) -> User:
        if user := User.objects.filter(username=self.cpf).first():
            return user
        nome, sobrenome = self.nome.split(" ", 1)
        self.created_password = default_user_password(
            self.cpf, self.nome, self.data_nascimento
        )
        user = User.objects.create_user(
            username=self.cpf,
            first_name=nome,
            last_name=sobrenome,
            password=self.created_password,
        )
        logging.getLogger("Pessoa").info("Usuário {user} criado para pessoa {self}")
        return user

    def clean(self):
        # Nome completo
        palavras = [n for n in self.nome.split(" ") if n]
        if len(palavras) < 2:
            raise ValidationError("Nome da pessoa deve incluir ao menos um sobrenome")
        self.is_cleaned = True

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean()

        self.nome_busca = nome_pesquisavel(self.nome)
        super().save(*args, **kwargs)
        _ = self.get_user()

    class Meta:
        permissions = roles.pessoa_roles


class Veiculo(models.Model):
    nome = models.CharField(verbose_name="Nome", max_length=40)
    imagem = models.ImageField(
        verbose_name="Imagem",
        upload_to=upload_to,
        help_text="Logotipo para ser usada nos relatórios",
    )
    capacidade = models.IntegerField(
        verbose_name="Capacidade",
        validators=[
            MinValueValidator(1, "Capacidade mínima"),
            MaxValueValidator(99, "Capacidade máxima"),
        ],
        help_text="Capacidade todal de pessoas",
    )
    qtd_staffs = models.IntegerField(
        verbose_name="Qtd Staffs", help_text="Inclui condutor e staffs"
    )
    qtd_max_criancas = models.IntegerField(verbose_name="Qtd Max Crianças", default=0)
    qtd_max_mulheres = models.IntegerField(verbose_name="Qtd Max Mulheres", default=99)
    qtd_max_homens = models.IntegerField(verbose_name="Qtd Max Homens", default=99)
    peso_total_max = models.IntegerField(
        verbose_name="Peso total máximo", default=0, help_text="kg"
    )
    peso_individual_max = models.IntegerField(
        verbose_name="Peso individual máximo", default=130, help_text="kg"
    )

    def save(self, *args, **kwargs) -> None:
        if self.peso_individual_max == 0:
            self.peso_individual_max = 130
        if self.peso_individual_max > 0 and self.peso_total_max == 0:
            self.peso_total_max = int(self.peso_individual_max * 0.8 * self.capacidade)

        if self.qtd_max_criancas > self.capacidade - self.qtd_staffs:
            self.qtd_max_criancas = self.capacidade - self.qtd_staffs
        if self.qtd_max_homens > self.capacidade:
            self.qtd_max_homens = self.capacidade
        if self.qtd_max_mulheres > self.capacidade:
            self.qtd_max_mulheres = self.capacidade

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nome


class Grupo(models.Model):
    nome = models.CharField(verbose_name="Nome", max_length=48)
    imagem = models.ImageField(verbose_name="Imagem", upload_to=upload_to)
    tipo_cobranca_traje = models.BooleanField(verbose_name="Cobrar traje", default=True)
    anfitrioes = models.ManyToManyField(
        Pessoa, verbose_name="Anfitriões", related_name="grupo_anfitriao"
    )

    def __str__(self):
        return self.nome


class SituacaoDesfileChoices(models.TextChoices):
    ABERTO = "A", "Aberto"
    CONFIRMADO = "C", "Confirmado"
    CANCELADO = "X", "Cancelado"
    TERMINADO = "T", "Terminado"


class Desfile(models.Model):
    is_cleaned = False

    nome = models.CharField(verbose_name="Nome", max_length=64)
    local = models.CharField(verbose_name="Local", max_length=64, default="")
    data = models.DateField(verbose_name="Data")
    veiculos = models.ManyToManyField(Veiculo)
    confirmado = models.BooleanField(
        verbose_name="Confirmado",
        default=False,
        help_text="Desfiles confirmados não podem ter seus dados alterados",
    )
    aprovador = models.ForeignKey(
        User, verbose_name="Aprovador", blank=True, null=True, on_delete=models.PROTECT
    )
    data_aprovacao = models.DateTimeField(
        verbose_name="Data aprovação", blank=True, null=True
    )
    obs: str = models.TextField(
        verbose_name="Observações",
        max_length=512,
        default="",
        help_text="Observações internas do desfile",
    )
    obs_convidado: str = models.TextField(
        verbose_name="Observações para o convidado",
        max_length=512,
        default="",
        help_text="Observações que serão adicionadas ao convite e mostradas no painel do convidado",
    )

    situacao = models.CharField(
        verbose_name="Situação",
        max_length=1,
        choices=SituacaoDesfileChoices,
        default=SituacaoDesfileChoices.ABERTO,
    )

    valor_taxa_traje: decimal.Decimal = models.DecimalField(
        verbose_name="Taxa do traje",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=decimal.Decimal(0),
    )

    def __str__(self) -> str:
        return f"{self.nome} em {self.local}: {self.data:%d/%m/%Y}"

    def clean(self):
        if self.id and not self.veiculos.first():
            raise ValidationError("É necessário incluir ao menos um veículo no desfile")
        self.is_cleaned = True

    def save(self, *args, **kwargs) -> None:
        if not self.is_cleaned:
            self.clean()

        if not self.confirmado:
            self.aprovador = None
            self.data_aprovacao = None
            self.situacao = SituacaoDesfileChoices.ABERTO
        elif not self.data_aprovacao:
            self.data_aprovacao = DateTimeProvider.now()
            self.situacao = SituacaoDesfileChoices.CONFIRMADO

        if self.situacao == SituacaoDesfileChoices.ABERTO and self.confirmado:
            self.situacao = SituacaoDesfileChoices.CONFIRMADO

        if self.valor_taxa_traje == decimal.Decimal(0):
            if ultimo_desfile := Desfile.objects.order_by("-data").first():
                self.valor_taxa_traje = ultimo_desfile.valor_taxa_traje

        return super().save(*args, **kwargs)


class VeiculoDesfile(models.Model):
    desfile = models.ForeignKey(
        Desfile, verbose_name="Desfile", on_delete=models.PROTECT
    )
    veiculo = models.ForeignKey(
        Veiculo, verbose_name="Veículo", on_delete=models.PROTECT
    )


class InscricaoDesfile(models.Model):
    is_cleaned = False

    desfile = models.ForeignKey(
        Desfile, verbose_name="Desfile", on_delete=models.PROTECT
    )
    pessoa = models.ForeignKey(Pessoa, verbose_name="Pessoa", on_delete=models.PROTECT)
    tipo_pessoa = models.CharField(
        verbose_name="Tipo",
        max_length=1,
        choices=TiposPessoasChoices,
        default=TiposPessoasChoices.CONVIDADO,
    )
    veiculo = models.ForeignKey(
        VeiculoDesfile,
        verbose_name="Veículo",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    aprovacao = models.CharField(
        verbose_name="Aprovação",
        max_length=1,
        choices=AprovacaoChoices,
        default=AprovacaoChoices.PENDENTE,
    )
    aprovador = models.ForeignKey(
        User, verbose_name="Aprovador", blank=True, null=True, on_delete=models.PROTECT
    )
    data_aprovacao = models.DateTimeField(
        verbose_name="Data aprovação", blank=True, null=True
    )
    convite: "Convite" = models.ForeignKey(
        "Convite",
        verbose_name="Convite",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    grupo: Grupo = models.ForeignKey(
        Grupo, verbose_name="Grupo", on_delete=models.PROTECT, null=True, blank=True
    )
    data_desfile: datetime.date = models.DateField(
        verbose_name="Data do desfile", null=True, blank=True
    )

    class Meta:
        unique_together = ("desfile", "pessoa")

    def clean(self) -> None:
        if (
            self.aprovador
            and self.data_aprovacao
            and self.aprovacao == AprovacaoChoices.PENDENTE
        ):
            raise ValidationError("Estado de aprovação não pode ser pendente")
        if self.aprovacao == AprovacaoChoices.APROVADO and not self.veiculo:
            raise ValidationError("A inscrição para o desfile deve indicar um veículo")

        self.is_cleaned = True
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        if not self.is_cleaned:
            self.clean()

        self.data_desfile = self.desfile.data

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.pessoa} -> {self.desfile} : {self.status_aprovacao()}"

    def status_aprovacao(
        self, amigavel: bool = False, incluir_desfile: bool = False
    ) -> str:
        match self.aprovacao:
            case AprovacaoChoices.APROVADO:
                status = f"✅ Aprovado por {self.aprovador}"
            case AprovacaoChoices.REJEITADO:
                status = (
                    "🙄 Verifique a situação do seu convite com um administrador"
                    if amigavel
                    else f"⛔ Rejeitado por {self.aprovador}"
                )
            case _:
                status = "⏳ Aprovação pendente"

        return f"{status} : {self.desfile}" if incluir_desfile else status


class StaffPadrao(models.Model):
    is_cleaned = False
    staff_padrao_veiculo: "StaffPadraoVeiculo" = models.ForeignKey(
        "StaffPadraoVeiculo", verbose_name="staff padrão", on_delete=models.PROTECT
    )
    pessoa: Pessoa = models.OneToOneField(
        Pessoa, verbose_name="Pessoa", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.pessoa} [{self.pessoa.get_tipo_display()}]"

    def clean(self):
        if self.pessoa.tipo == TiposPessoasChoices.CONVIDADO:
            raise ValidationError(
                "Staff padrão não pode ser uma pessoa do tipo convidado"
            )
        self.is_cleaned = True

    def save(self, *args, **kwargs) -> None:
        if not self.is_cleaned:
            self.clean()

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Staffs padrão"
        verbose_name = "Staff padrão"
        unique_together = ("staff_padrao_veiculo", "pessoa")


class StaffPadraoVeiculo(models.Model):
    veiculo: Veiculo = models.OneToOneField(
        Veiculo,
        verbose_name="Veículo",
        primary_key=True,
        on_delete=models.PROTECT,
    )

    ultimo_ajuste: datetime = models.DateTimeField(
        verbose_name="Último ajuste", auto_now=True, editable=False
    )
    usuario: User = models.ForeignKey(
        User, verbose_name="Responsável", on_delete=models.PROTECT
    )

    pessoas = models.ManyToManyField(StaffPadrao, verbose_name="Pessoas")

    def __str__(self):
        return f"{self.veiculo}"

    class Meta:
        verbose_name_plural = "Staffs padrão por veículo"
        verbose_name = "Staff padrão por veículo"


class PessoaStaff(Pessoa):
    is_cleaned = False

    class Meta:
        proxy = True
        verbose_name_plural = "Pessoas staff"
        verbose_name = "Pessoa staff"

    def clean(self):
        if self.tipo == TiposPessoasChoices.CONVIDADO:
            raise ValidationError("Pessoa staff não pode ser do tipo convidado")
        self.is_cleaned = True

    def save(self, *args, **kwargs) -> None:
        if not self.is_cleaned:
            self.clean()
        return super().save(*args, **kwargs)

    @property
    def staff_padrao_veiculo(self) -> StaffPadraoVeiculo | None:
        if padrao := StaffPadrao.objects.filter(pessoa=self).first():
            return padrao.staff_padrao_veiculo


def extract_campos_checklist(campos_checklist: str) -> str:
    linhas = [
        linha.strip()
        for linha in (campos_checklist or "").splitlines(keepends=False)
        if linha.strip()
    ]
    return "\n".join(linhas)


def campos_checklist_validator(value):
    if not extract_campos_checklist(value):
        raise ValidationError(
            "Lista de verificação deve ter ao menos uma linha indicando um item a ser verificado"
        )


class Traje(models.Model):
    is_cleaned = False

    nome: str = models.CharField(verbose_name="Nome", max_length=48)
    veiculo: Veiculo = models.ForeignKey(
        Veiculo, verbose_name="Veículo", blank=True, null=True, on_delete=models.PROTECT
    )
    genero: GenerosChoices = models.CharField(
        verbose_name="Gênero", max_length=1, choices=GenerosChoices
    )
    campos_checklist: str = models.TextField(
        verbose_name="Lista de verificação",
        max_length=2048,
        blank=True,
        default="",
        help_text="Cada linha é um ítem a ser verificado na entrega e devolução do traje",
        validators=[campos_checklist_validator],
    )

    def clean(self):
        if not extract_campos_checklist(self.campos_checklist):
            raise ValidationError(
                "Lista de verificação deve ter ao menos uma linha indicando um item a ser verificado"
            )
        self.is_cleaned = True

    def __str__(self) -> str:
        return self.nome + (f" ({self.veiculo})" if self.veiculo else "")

    def save(self, *args, **kwargs) -> None:
        if not self.is_cleaned:
            self.clean()

        self.campos_checklist = extract_campos_checklist(self.campos_checklist)
        return super().save(*args, **kwargs)


class TrajeInventario(models.Model):
    num_inventario: int = models.IntegerField(
        verbose_name="# Inventário",
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
    )
    traje: Traje = models.ForeignKey(
        Traje, verbose_name="Traje", on_delete=models.PROTECT
    )
    tamanho: TamanhosTrajeChoices = models.CharField(
        verbose_name="Tamanho", choices=TamanhosTrajeChoices, max_length=1
    )
    situacao: SituacaoTrajeChoices = models.CharField(
        verbose_name="Situação",
        max_length=1,
        choices=SituacaoTrajeChoices,
        editable=False,
    )
    usuario: User = models.ForeignKey(
        User,
        verbose_name="Responsável",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    pessoa: Pessoa = models.ForeignKey(
        Pessoa, verbose_name="Pessoa", on_delete=models.PROTECT, null=True, blank=True
    )
    ultima_atualizacao: datetime = models.DateTimeField(
        verbose_name="Última atualização", auto_now=True
    )

    def __str__(self) -> str:
        return f"#{self.num_inventario} {self.traje}"

    def get_checklist_itens(self) -> list[str]:
        traje_checks = set(
            extract_campos_checklist(self.traje.campos_checklist).splitlines(False)
        )
        return list(traje_checks)

    def situacao_str(self) -> str:
        """Descrição da situação atual do traje"""
        match self.situacao:
            case SituacaoTrajeChoices.DISPONIVEL:
                return f"{self} : Disponível"
            case SituacaoTrajeChoices.EMPRESTADO:
                return f"{self} : Emprestado a {self.pessoa}"
            case SituacaoTrajeChoices.MANUTENCAO:
                return f"{self} : Em manutenção"
            case SituacaoTrajeChoices.EXTRAVIADO:
                return f"{self} : Extraviado"
            case SituacaoTrajeChoices.DESCARTADO:
                return f"{self} : Descartado"

    def save(self, *args, **kwargs) -> None:
        criar_entrada = not self.id
        super().save(*args, **kwargs)
        if criar_entrada:
            TrajeHistorico.objects.create(
                traje=self,
                obs="Entrada automática",
                movimento=TrajeMovimentoChoices.ENTRADA,
                usuario=get_robot_user(),
            )

    class Meta:
        verbose_name = "Inventário"
        verbose_name_plural = "Inventários"


class TrajeHistorico(models.Model):
    is_cleaned = False
    traje: TrajeInventario = models.ForeignKey(
        TrajeInventario, verbose_name="Traje", on_delete=models.PROTECT
    )
    data: datetime.datetime = models.DateTimeField(
        verbose_name="Data", auto_now_add=True
    )
    obs: str = models.TextField(verbose_name="Observações", max_length=120, default="")
    movimento: TrajeMovimentoChoices = models.CharField(
        verbose_name="Movimento", max_length=1, choices=TrajeMovimentoChoices
    )
    usuario: User = models.ForeignKey(
        User, verbose_name="Responsável atual", on_delete=models.PROTECT
    )
    pessoa: Pessoa = models.ForeignKey(
        Pessoa,
        verbose_name="Pessoa atual",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    checagem = models.ManyToManyField(
        "TrajeHistoricoChecklistItem", verbose_name="Checagem"
    )

    def __str__(self) -> str:
        return f"{self.traje}: {self.get_movimento_display()}"

    def get_checklist_itens(self) -> list[str]:
        traje_checks = set(
            extract_campos_checklist(self.traje.traje.campos_checklist).splitlines(
                False
            )
        )
        return list(traje_checks)

    def update_checagem(self):
        """Checagem deve ocorrer no momento do emprestimo e na devolução"""
        if self.movimento in [
            TrajeMovimentoChoices.EMPRESTIMO,
            TrajeMovimentoChoices.DEVOLUCAO,
        ]:
            traje_checks = set(
                extract_campos_checklist(self.traje.traje.campos_checklist).splitlines(
                    False
                )
            )
            # Procura por checks que não existem na lista esperada
            if checks := self.checagem.filter(~models.Q(item__in=traje_checks)):
                self.checagem.remove(checks)

            # Procura por checks da lista que não estão na instância
            checks = set(check.item for check in self.checagem.all())
            novos_checks = traje_checks.difference(checks)
            self.checagem.add(
                *[
                    TrajeHistoricoChecklistItem.objects.create(
                        historico=self, item=check
                    )
                    for check in novos_checks
                ]
            )

        else:
            if checks := self.checagem.objects.all():
                # Remover qualquer checagem anterior
                self.checagem.remove(checks)

    def clean(self):
        # Verifica a situação do último histórico se for um insert
        if self.id:
            ultimo = (
                TrajeHistorico.objects.filter(traje=self.traje, data__lt=self.data)
                .order_by("data")
                .last()
            )
        else:
            ultimo = (
                TrajeHistorico.objects.filter(traje=self.traje).order_by("data").last()
            )

        if not ultimo:
            # O primeiro histórico deve ser uma entrada
            if self.movimento != TrajeMovimentoChoices.ENTRADA:
                raise ValidationError(
                    "O primeiro histórico de um traje no inventário deve ser uma ENTRADA"
                )
        else:
            # O movimento deve ser diferente do movimento anterior
            if self.movimento == ultimo.movimento:
                raise ValidationError(
                    f"O movimento deve ser diferente do anterior: {self.get_movimento_display()}"
                )
            # trajes descartados ou extraviados não podem mais ser movimentados
            if ultimo.movimento in [
                TrajeMovimentoChoices.DESCARTE,
                TrajeMovimentoChoices.EXTRAVIO,
            ]:
                raise ValidationError(
                    f"Não é possível gerar movimento de um traje em situação: {ultimo.get_movimento_display()}"
                )

            allowed = {
                TrajeMovimentoChoices.ENTRADA: [
                    TrajeMovimentoChoices.EMPRESTIMO,
                    TrajeMovimentoChoices.MANUTENCAO,
                    TrajeMovimentoChoices.DESCARTE,
                    TrajeMovimentoChoices.EXTRAVIO,
                ],
                TrajeMovimentoChoices.EMPRESTIMO: [
                    TrajeMovimentoChoices.DEVOLUCAO,
                    TrajeMovimentoChoices.EXTRAVIO,
                ],
                TrajeMovimentoChoices.DESCARTE: [],
                TrajeMovimentoChoices.EXTRAVIO: [],
                TrajeMovimentoChoices.DEVOLUCAO: [
                    TrajeMovimentoChoices.EMPRESTIMO,
                    TrajeMovimentoChoices.MANUTENCAO,
                    TrajeMovimentoChoices.DESCARTE,
                    TrajeMovimentoChoices.EXTRAVIO,
                ],
                TrajeMovimentoChoices.MANUTENCAO: [
                    TrajeMovimentoChoices.DEVOLUCAO,
                    TrajeMovimentoChoices.DESCARTE,
                    TrajeMovimentoChoices.EXTRAVIO,
                ],
            }[ultimo.movimento]

            if self.movimento not in allowed:
                raise ValidationError(
                    f"O movimento deve ser uma das opções a seguir: {', '.join(a.label for a in allowed)}"
                )
        situacao = {
            TrajeMovimentoChoices.ENTRADA: SituacaoTrajeChoices.DISPONIVEL,
            TrajeMovimentoChoices.EMPRESTIMO: SituacaoTrajeChoices.EMPRESTADO,
            TrajeMovimentoChoices.MANUTENCAO: SituacaoTrajeChoices.MANUTENCAO,
            TrajeMovimentoChoices.DEVOLUCAO: SituacaoTrajeChoices.DISPONIVEL,
            TrajeMovimentoChoices.DESCARTE: SituacaoTrajeChoices.DESCARTADO,
            TrajeMovimentoChoices.EXTRAVIO: SituacaoTrajeChoices.EXTRAVIADO,
        }
        if (
            self.movimento == TrajeMovimentoChoices.EMPRESTIMO
            and self.traje.traje.genero != self.pessoa.genero
        ):
            raise ValidationError(
                f"Este traje só pode ser emprestado para pessoas do gênero {self.traje.traje.get_genero_display()}"
            )

        self.traje.situacao = situacao[self.movimento]
        self.traje.pessoa = self.pessoa
        self.traje.usuario = self.usuario
        self.traje.ultima_atualizacao = self.data
        self.traje.save()
        self.is_cleaned = True

    def save(self, *args, **kwargs) -> None:
        if not self.is_cleaned:
            self.clean()
        result = super().save(*args, **kwargs)
        self.update_checagem()
        return result

    class Meta:
        verbose_name = "Histórico do traje"
        verbose_name_plural = "Históricos do traje"


class TrajeTaxa(models.Model):
    desfile: Desfile = models.ForeignKey(
        Desfile, verbose_name="Desfile", on_delete=models.PROTECT
    )
    traje: TrajeHistorico = models.ForeignKey(
        TrajeHistorico, verbose_name="Histórico", on_delete=models.PROTECT
    )
    valor_taxa: decimal.Decimal = models.DecimalField(
        verbose_name="R$ taxa",
        max_digits=10,
        decimal_places=2,
        default=decimal.Decimal(0),
        validators=[MinValueValidator(0)],
    )
    valor_pago: decimal.Decimal = models.DecimalField(
        verbose_name="R$ pago",
        max_digits=10,
        decimal_places=2,
        default=decimal.Decimal(0),
        validators=[MinValueValidator(0)],
    )
    data_pagamento: datetime.date = models.DateField(
        verbose_name="Data Pagamento", null=True, blank=True
    )
    usuario: User = models.ForeignKey(
        User, verbose_name="Responsável", on_delete=models.PROTECT
    )
    situacao: TrajeSituacaoTaxa = models.CharField(
        verbose_name="Situação",
        max_length=1,
        choices=TrajeSituacaoTaxa,
        default=TrajeSituacaoTaxa.PENDENTE,
    )

    def __str__(self):
        if self.situacao == TrajeSituacaoTaxa.PENDENTE:
            if self.valor_taxa > 0:
                return "Sem taxa"
            return "Taxa pendente"
        if self.situacao == TrajeSituacaoTaxa.PAGO:
            return "Paga"
        return "Abonada"


class TrajeHistoricoChecklistItem(models.Model):
    historico: TrajeHistorico = models.ForeignKey(
        TrajeHistorico, verbose_name="Histórico", on_delete=models.PROTECT
    )
    item: str = models.CharField(
        verbose_name="Item", max_length=40, blank=False, null=False
    )
    checado: bool = models.BooleanField(verbose_name="Checado", default=False)

    def __str__(self):
        return f"{self.item}: {'✅' if self.checado else '❌'}"


class Convite(models.Model):
    desfile: Desfile = models.ForeignKey(
        Desfile, verbose_name="Desfile", on_delete=models.PROTECT
    )
    grupo: Grupo = models.ForeignKey(
        Grupo, verbose_name="Grupo", on_delete=models.PROTECT
    )
    valido_ate: datetime.date = models.DateField(
        verbose_name="Válido até",
        default=datetime.date.min,
    )
    usuario: User = models.ForeignKey(
        User, verbose_name="Responsável", on_delete=models.PROTECT
    )
    data: datetime.datetime = models.DateTimeField(
        verbose_name="Criação", auto_now_add=True
    )
    max_convidados: int = models.PositiveSmallIntegerField(
        verbose_name="Máximo de convidados", default=20
    )
    hash: str = models.CharField(
        verbose_name="Hash", max_length=8, editable=False, default=""
    )
    convidados_confirmados: int = models.PositiveSmallIntegerField(
        verbose_name="Confirmados", default=0
    )

    def save(self, *args, **kwargs) -> None:
        if self.valido_ate == datetime.date.min:
            self.valido_ate = datetime.date.today() + datetime.timedelta(hours=24 * 30)
        if not self.hash:
            self.hash = convite_hash()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Convite para {self.desfile}"


class ConfigChoices(models.TextChoices):
    PESSOA_CADASTRO_HABILITADO = ("pes.cad.hab", "Cadastro de pessoas habilitado")


class Config(models.Model):
    name: str = models.CharField(max_length=20, primary_key=True, choices=ConfigChoices)
    value = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.get_name_display()} = {self.value}"

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"


class UserMessageLevelChoices(models.TextChoices):
    INFO = "I", "Informação"
    WARN = "W", "Alerta"
    ERROR = "E", "Erro"


class UserMessage(models.Model):
    user_from: User = models.ForeignKey(
        User,
        verbose_name="Remetente",
        on_delete=models.PROTECT,
        related_name="user_from",
        editable=False,
    )
    user_to: User = models.ForeignKey(
        User,
        verbose_name="Destinatário",
        on_delete=models.PROTECT,
        related_name="user_to",
        editable=False,
    )
    when: datetime.datetime = models.DateTimeField(
        verbose_name="Quando", auto_now_add=True, editable=False
    )
    title: str = models.CharField(verbose_name="Título", max_length=40)
    message: str = models.CharField(verbose_name="Mensagem", max_length=250)
    read_at: datetime.datetime = models.DateTimeField(
        verbose_name="Lida", null=True, blank=True, editable=False
    )
    level: str = models.CharField(
        verbose_name="Nível",
        max_length=1,
        choices=UserMessageLevelChoices,
        default=UserMessageLevelChoices.INFO,
    )
    link: str = models.CharField(
        verbose_name="Link", max_length=128, null=True, blank=True
    )

    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        indexes = [models.Index(fields=["user_to", "when"], name="idx_msg")]

    def __str__(self):
        return f"{self.when:%d/%m/%Y %H:%M} {self.get_level_display()} {self.user_from} : {self.message}"

    @property
    def class_color(self) -> str:
        match self.level:
            case UserMessageLevelChoices.WARN:
                return "warning"
            case UserMessageLevelChoices.ERROR:
                return "danger"
        return "info"

    @property
    def full_link(self) -> str:
        return self.link or (
            ""
            if not self.id
            else reverse(
                "admin:{}_{}_change".format(
                    self._meta.app_label, self._meta.model_name
                ),
                args=(self.pk,),
            )
        )


def create_guid() -> str:
    """Create a UUID with length 36"""
    return str(uuid.uuid1())


class PessoaRevisarSenha(models.Model):
    guid: str = models.CharField(
        verbose_name="GUID", max_length=36, default=create_guid, primary_key=True
    )
    pessoa: Pessoa = models.ForeignKey(
        Pessoa, verbose_name="Pessoa", on_delete=models.PROTECT, editable=False
    )
    data_solicitacao: datetime = models.DateTimeField(
        verbose_name="Data solicitação", auto_now_add=True
    )
    atendida_por: User = models.ForeignKey(
        User,
        verbose_name="Atendida por",
        on_delete=models.PROTECT,
        editable=False,
        blank=True,
        null=True,
    )
    atendida_em: datetime = models.DateTimeField(
        verbose_name="Atendida em", blank=True, null=True
    )
    ativa: bool = models.BooleanField(verbose_name="Ativa", default=True)

    def __str__(self):
        return f"{self.pessoa} @ {self.data_solicitacao:%d/%m/%Y %H:%M}" + (
            ""
            if not self.atendida_em
            else f" atendida por {self.atendida_por} [{self.atendida_em:%d/%m/%Y %H:%M}]"
        )

    class Meta:
        verbose_name = "Revisão de senha"
        verbose_name_plural = "Revisões de senha"


class PessoaLocalizacao(models.Model):
    when: datetime.datetime = models.DateTimeField(
        verbose_name="Quando", auto_now_add=True, editable=False
    )
    pessoa: Pessoa = models.ForeignKey(
        Pessoa, verbose_name="Pessoa", on_delete=models.PROTECT, editable=False
    )
    ip: str = models.GenericIPAddressField(verbose_name="IP")
    pais: str = models.CharField(verbose_name="País", max_length=20)
    estado: str = models.CharField(verbose_name="Estado", max_length=30)
    cidade: str = models.CharField(verbose_name="Cidade", max_length=30)

    class Meta:
        indexes = [models.Index(fields=["pessoa", "when"], name="idx_loc")]
        verbose_name = "Localização"
        verbose_name_plural = "Localizações"

    def __str__(self):
        return f"{self.pessoa} [{self.ip} : {self.pais}|{self.estado}|{self.cidade}] @ {self.when:%d/%m/%Y %H:%M}"
