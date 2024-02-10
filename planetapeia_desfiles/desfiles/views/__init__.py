import base64
import pickle

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlencode

from ..models import Desfile
from ..navbar import NavBar

# Create your views here.


def index(request):
    return HttpResponse("OK")


def convite_view(request: HttpRequest):
    navbar = (
        NavBar()
        .link("#", "Início", True)
        .link("#", "Atalho")
        .sublink("#", "Sub item 1")
        .sublink("#", "-")
        .sublink("#", "Sub item 2")
        .link("#", "Desabilitada", disabled=True)
    ).to_html()
    return render(
        request,
        "convite.html",
        context={
            "title": "Planetapéia - Convite",
            "header": f"Convite para o desfile {Desfile.objects.first()}",
            "navbar": navbar,
            "desfile": Desfile.objects.first(),
        },
    )


def reverse_querystring(
    view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None
):
    """Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'})
    """
    base_url = reverse(
        view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app
    )
    if query_kwargs:
        return "{}?{}".format(base_url, urlencode(query_kwargs))
    return base_url


def reverse_crypto_query(
    view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None
):
    if query_kwargs:
        query_kwargs = {"q": encrypt_dict(query_kwargs)}
    return reverse_querystring(view, urlconf, args, kwargs, current_app, query_kwargs)


def encrypt_dict(data: dict) -> str:
    return base64.b64encode(pickle.dumps(data)).decode()


def decrypt_dict(encrypted: str) -> dict:
    return pickle.loads(base64.b64decode(encrypted))


def decrypt_query_string(request: HttpRequest) -> dict:
    if q := request.GET.get("q") or request.headers.get("xpto_q"):
        return decrypt_dict(q)
    return {}
