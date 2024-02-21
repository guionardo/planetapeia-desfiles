from django.contrib import admin

from .admins.convite import ConviteAdmin
from .admins.desfile import DesfileAdmin
from .admins.grupo import GrupoAdmin
from .admins.inscricao_desfile import InscricaoDesfileAdmin
from .admins.pessoa import PessoaAdmin
from .admins.staff import StaffPadraoVeiculoAdmin, StaffsAdmin
from .admins.traje import TrajeAdmin, TrajeInventarioAdmin
from .admins.user_messages import UserMessagesAdmin
from .admins.veiculo import VeiculoAdmin
from .admins.config import ConfigAdmin
from .models import (
    Config,
    Convite,
    Desfile,
    Grupo,
    InscricaoDesfile,
    Pessoa,
    PessoaStaff,
    StaffPadraoVeiculo,
    Traje,
    TrajeInventario,
    UserMessage,
    Veiculo,
)


admin.site.register(Config, ConfigAdmin)

admin.site.register(Pessoa, PessoaAdmin)
admin.site.register(PessoaStaff, StaffsAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(StaffPadraoVeiculo, StaffPadraoVeiculoAdmin)
admin.site.register(Veiculo, VeiculoAdmin)
admin.site.register(Desfile, DesfileAdmin)

admin.site.register(Traje, TrajeAdmin)
admin.site.register(TrajeInventario, TrajeInventarioAdmin)

admin.site.register(Convite, ConviteAdmin)
admin.site.register(InscricaoDesfile, InscricaoDesfileAdmin)

admin.site.register(UserMessage, UserMessagesAdmin)

admin.site.site_title = "Planetapéia Desfiles"
admin.site.site_header = "Planetapéia Desfiles"