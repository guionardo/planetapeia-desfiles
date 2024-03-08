import datetime
import logging
import os
import struct

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unidecode import unidecode

from .services.date_time_provider import DateTimeProvider

robot_user: User = None


def cpf_validator(cpf):
    """Valida um CPF, retornando ValidationError em caso de erro"""

    numeros = [int(digito) for digito in str(cpf) if digito.isdigit()]

    if len(numeros) != 11:
        raise ValidationError("CPF inválido [número de dígitos deve ser 11]")

    soma_produtos = sum(a * b for a, b in zip(numeros[0:9], range(10, 1, -1)))
    digito_esperado = (soma_produtos * 10 % 11) % 10
    if numeros[9] != digito_esperado:
        raise ValidationError("CPF inválido")

    soma_produtos1 = sum(a * b for a, b in zip(numeros[0:10], range(11, 1, -1)))
    digito_esperado1 = (soma_produtos1 * 10 % 11) % 10
    if numeros[10] != digito_esperado1:
        raise ValidationError("CPF inválido")


def data_nascimento_validator(value):
    min_years = 2
    min_date = datetime.date(
        datetime.date.today().year - min_years,
        datetime.date.today().month,
        datetime.date.today().day,
    )
    if value > min_date:
        raise ValidationError(
            f"Data de nascimento deve ser anterior a {min_date:%d/%m/%Y}"
        )


def upload_to(instance, filename):
    _, ext = os.path.splitext(filename)
    if instance_id := instance.pk:
        ...
    else:
        cls = instance.__class__
        try:
            if latest := cls.objects.latest("pk"):
                instance_id = latest.pk + 1
            else:
                instance_id = 1
        except cls.DoesNotExist:
            instance_id = 1

    return f"uploads/{instance.__class__.__name__}_{instance_id}{ext}"


def daqui_a_30_dias() -> datetime.date:
    return datetime.date.today() + datetime.timedelta(hours=24 * 30)


def convite_hash() -> str:
    """Gerar um hash ordenado de 8 caracteres"""
    f = datetime.datetime.timestamp(DateTimeProvider.now())
    return hex(struct.unpack("<I", struct.pack("<f", f))[0])[2:].upper()


def get_robot_user():
    global robot_user
    if robot_user:
        return robot_user
    robot_username = "planetapeia"
    if robot_user := User.objects.filter(username=robot_username).first():
        return robot_user
    robot_user = User.objects.create_superuser(
        username=robot_username, first_name="🤖 Planetabot"
    )
    logging.info("Created robot user: %s", robot_user)
    return robot_user


def default_user_password(
    cpf: str, nome: str, data_nascimento: datetime.date | str
) -> str:
    if isinstance(data_nascimento, str):
        data_nascimento = datetime.datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    iniciais = "".join(w[0] for w in nome.upper().split(" ") if w)
    return f"{iniciais}{cpf[-4:]}{data_nascimento.year}"


def get_pessoa_name(quem) -> str:
    """Obtém o nome da pessoa ou usuário informado"""
    from .models import Pessoa

    if isinstance(quem, Pessoa):
        user = quem.get_user()
        name = user.get_username()
    elif isinstance(quem, User):
        user = quem
        name = quem.get_full_name() or quem.get_username()
    else:
        raise ValueError(f"Esperado Pessoa ou User, obtido {quem.__class__}: {quem}")

    if not user.is_active:
        return "anônimo"
    return ("🦸 " if user.is_superuser else "🧑🏻‍💻 " if user.is_staff else "") + name


def nome_pesquisavel(nome: str | None) -> str:
    """Transforma um nome, retirando acentos e convertendo em minúsculas para facilitar a consulta"""
    return " ".join(
        [n.strip() for n in unidecode(nome or "").lower().split(" ") if n.strip()]
    )
