""" Views de trajes """
from django.urls import path

from .trajes_index import TrajesIndex
from .trajes_op import TrajesOp

paths = [
    path("trajes", TrajesIndex.as_view(), name="trajes_index"),
    path(
        "trajes/<int:num_inventario>",
        TrajesOp.as_view(),
        {"op": "op"},
        name="trajes_op",
    ),
    path(
        "trajes/devolucao/<int:num_inventario>",
        TrajesOp.as_view(),
        {"op": "devolucao"},
        name="traje_devolucao",
    ),
    path(
        "trajes/emprestimo/<int:num_inventario>/<str:pessoa_id>/",
        TrajesOp.as_view(),
        {"op": "emprestimo"},
        name="traje_emprestimo",
    ),
    path(
        "trajes/saida/<int:num_inventario>",
        TrajesOp.as_view(),
        {"op": "saida"},
        name="traje_saida",
    ),
]
