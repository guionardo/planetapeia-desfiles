from django.core.exceptions import ValidationError
import datetime
import decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .models_utils import (
    convite_hash,
    cpf_validator,
    data_nascimento_validator,
    upload_to,
)


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


class TrajeMovimentoChoices(models.TextChoices):
    ENTRADA = "E", "Entrada"
    EMPRESTIMO = "B", "Empréstimo"
    DEVOLUCAO = "D", "Devolução"
    MANUTENCAO = "M", "Manutenção"
    DESCARTE = "X", "Descarte"


class TrajeSituacaoTaxa(models.TextChoices):
    PENDENTE = "P", "Pendente"
    PAGO = "$", "Pago"
    ABONADO = "A", "Abonado"


class Pessoa(models.Model):
    cpf = models.CharField(
        verbose_name="CPF", primary_key=True, max_length=11, validators=[cpf_validator]
    )
    nome = models.CharField(
        verbose_name="Nome",
        max_length=60,
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
        verbose_name="Tipo", max_length=1, choices=TiposPessoasChoices, default=TiposPessoasChoices.CONVIDADO
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

    def __str__(self):
        return self.nome


class Desfile(models.Model):
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

    def __str__(self) -> str:
        return f"{self.nome} em {self.local}: {self.data:%d/%m/%Y}"

    # def clean(self):
    #     if self.confirmado and not self.aprovador:
    #         self.confirmado = False
    #         raise ValidationError(
    #             "É necessário informar um aprovador para confirmar o desfile"
    #         )

    def save(self, *args, **kwargs) -> None:
        if not self.confirmado:
            self.aprovador = None
            self.data_aprovacao = None
        elif not self.data_aprovacao:
            self.data_aprovacao = datetime.datetime.now()

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
        verbose_name="Tipo", max_length=1, choices=TiposPessoasChoices, default=TiposPessoasChoices.CONVIDADO
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

    class Meta:
        unique_together = ("desfile", "pessoa")

    def clean(self) -> None:
        if (
            self.aprovador
            and self.data_aprovacao
            and self.aprovacao == AprovacaoChoices.PENDENTE
        ):
            raise ValidationError("Estado de aprovação não pode ser pendente")

        self.is_cleaned = True
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        if not self.is_cleaned:
            self.clean()

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        match self.aprovacao:
            case AprovacaoChoices.APROVADO:
                aprovacao = f"Aprovado por {self.aprovador}"
            case AprovacaoChoices.REJEITADO:
                aprovacao = f"Rejeitado por {self.aprovador}"
            case _:
                aprovacao = "Aprovação pendente"

        return f"{self.pessoa} -> {self.desfile} : {aprovacao}"


class Traje(models.Model):
    nome: str = models.CharField(verbose_name="Nome", max_length=48)
    veiculo: Veiculo = models.ForeignKey(
        Veiculo, verbose_name="Veículo", blank=True, null=True, on_delete=models.PROTECT
    )
    genero: GenerosChoices = models.CharField(
        verbose_name="Gênero", max_length=1, choices=GenerosChoices
    )

    def __str__(self) -> str:
        return self.nome + (f" ({self.veiculo})" if self.veiculo else "")


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
        verbose_name="Situação", max_length=1, choices=SituacaoTrajeChoices
    )

    def __str__(self) -> str:
        return f"#{self.num_inventario} {self.traje}"


class TrajeHistorico(models.Model):
    traje: TrajeInventario = models.ForeignKey(
        TrajeInventario, verbose_name="Traje", on_delete=models.PROTECT
    )
    data: datetime.datetime = models.DateTimeField(
        verbose_name="Data", auto_now_add=True
    )
    obs: str = models.CharField(verbose_name="Observações", max_length=120, default="")
    movimento: TrajeMovimentoChoices = models.CharField(
        verbose_name="Movimento", max_length=1, choices=TrajeMovimentoChoices
    )
    usuario: User = models.ForeignKey(
        User, verbose_name="Responsável", on_delete=models.PROTECT
    )
    pessoa: Pessoa = models.ForeignKey(
        Pessoa, verbose_name="Pessoa", on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.traje}: {self.movimento}"


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
