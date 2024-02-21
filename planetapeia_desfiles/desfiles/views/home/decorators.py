from django.http import HttpRequest


def just_admin(func):
    def wraped(request: HttpRequest):
        if request.user.is_staff:
            return func(request)

    return wraped
