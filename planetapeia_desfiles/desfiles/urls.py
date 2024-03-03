from .views import admin, auth, convite, home, perfil, root

urlpatterns = [
    *root.paths,
    *home.paths,
    *auth.paths,
    *perfil.paths,
    *convite.paths,
    *admin.paths,
]
