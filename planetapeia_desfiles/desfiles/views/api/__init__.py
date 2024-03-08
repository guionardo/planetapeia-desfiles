from django.urls import path

from .busca_pessoa import busca_pessoa


paths = [
    path("api/busca_pessoa", busca_pessoa, name="api_busca_pessoa"),
]
