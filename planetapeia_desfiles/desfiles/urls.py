from .views import admin, api, auth, convite, home, perfil, root, trajes

urlpatterns = [
    *root.paths,
    *home.paths,
    *auth.paths,
    *perfil.paths,
    *convite.paths,
    *admin.paths,
    *trajes.paths,
    *api.paths,
]
