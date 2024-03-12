""" Views de trajes """
from django.urls import path

from .trajes_devolucao import TrajesDevolucao
from .trajes_emprestimo import TrajesEmprestimo
from .trajes_entrega_pessoa import TrajesEntregaPessoa
from .trajes_index import TrajesIndex
from .trajes_op import TrajesOp

paths = [
    path("trajes", TrajesIndex.as_view(), name="trajes_index"),
    path(
        "trajes/entrega/<str:cpf>",
        TrajesEntregaPessoa.as_view(),
        name="trajes_entrega_pessoa",
    ),
    path(
        "trajes/<int:num_inventario>",
        TrajesOp.as_view(),
        {"op": "op"},
        name="trajes_op",
    ),
    path(
        "trajes/devolucao/<int:num_inventario>",
        TrajesDevolucao.as_view(),
        name="traje_devolucao",
    ),
    path(
        "trajes/emprestimo/<int:num_inventario>/<str:pessoa_id>/",
        TrajesOp.as_view(),
        {"op": "emprestimo"},
        name="traje_emprestimo",
    ),
    path(
        "trajes/emprestimo/checagem/<int:num_inventario>/<str:pessoa_id>/",
        TrajesEmprestimo.as_view(),
        name="traje_emprestimo_checagem",
    ),
    path(
        "trajes/saida/<int:num_inventario>",
        TrajesOp.as_view(),
        {"op": "saida"},
        name="traje_saida",
    ),
]
