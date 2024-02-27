from datetime import timedelta

import httpx
from django.http.request import HttpRequest

from ..services import location
from ..services.location import IPLocation, update_location_pessoa
from ..services.mem_cache import MemCache


class LocationMiddleware:
    """Injeção do objeto pessoa logada na requisição"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.ips = MemCache(default_ttl=timedelta(hours=1))

    def __call__(self, request: HttpRequest):
        if request.pessoa:
            ip = location.get_ip_from_request(request)
            if not (loc := self.ips.get(ip)):
                response = httpx.get(f"http://ip-api.com/json/{ip}")
                if response.status_code < 300:
                    loc = IPLocation.from_dict(response.json())
                    self.ips.set(ip, loc)

            request.location = loc
            update_location_pessoa(request.pessoa, loc)
        else:
            request.location = IPLocation()

        return self.get_response(request)
