""" Views de raiz """
from django.urls import path

from .index import Index

paths = [
    path("", Index.as_view(), name="index"),
]
