__all__ = ["NavBar"]
from django.http.request import HttpRequest

from ...models import GenerosChoices
from .navbar import NavBar


def get_post_data(request: HttpRequest, *variables, default_empty=""):
    return (request.POST.get(var, default_empty) for var in variables)


def use_genero(
    request: HttpRequest, prefixo: str, sufixo_masc: str = "o", sufixo_fem: str = "a"
) -> str:
    """Monta uma palavra como sufixo de acordo com o genero da pessoa"""
    if request.pessoa:
        return f"{prefixo}{sufixo_masc if request.pessoa.genero==GenerosChoices.MASCULINO else sufixo_fem}"
    return f"{prefixo}{sufixo_masc}"
