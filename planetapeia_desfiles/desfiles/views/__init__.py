from django.http import HttpRequest


def get_post_data(request: HttpRequest, *keys) -> tuple:
    return (request.POST.get(key, None) for key in keys)
