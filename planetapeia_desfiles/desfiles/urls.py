from django.urls import path

from .views import index
from .views.cadastro import CadastroPessoaView
from .views.convite import ConviteView

urlpatterns = [
    # ex: /polls/
    path("", index, name="index"),
    path("convite/<str:hash>", ConviteView.as_view(), name="convite"),
    path("cadastro/pessoa", CadastroPessoaView.as_view(), name="cadastro_pessoa"),
    # # ex: /polls/5/
    # path("<int:question_id>/", views.detail, name="detail"),
    # # ex: /polls/5/results/
    # path("<int:question_id>/results/", views.results, name="results"),
    # # ex: /polls/5/vote/
    # path("<int:question_id>/vote/", views.vote, name="vote"),
]
