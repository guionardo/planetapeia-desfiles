from django import template
from django.contrib.auth.models import User
from django.template.defaultfilters import stringfilter

from ..models import Pessoa
from ..models_utils import get_pessoa_name

register = template.Library()


@register.filter
@stringfilter
def user_full_name(user: User | Pessoa) -> str:
    try:
        nome = get_pessoa_name(user)
        return nome
    except ValueError:
        return user
