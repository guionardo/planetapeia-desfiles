import inspect
import logging
import time
from dataclasses import dataclass, field

import httpx
from django.http.request import HttpRequest

from ..models import Pessoa, PessoaLocalizacao

_external_ip = (0, "")


@dataclass(match_args=False)
class IPLocation:
    status: str = field(default="unknown")
    country: str = field(default="")
    countryCode: str = field(default="")
    region: str = field(default="")
    regionName: str = field(default="")
    city: str = field(default="")
    zip: str = field(default="")
    lat: float = field(default=0)
    lon: float = field(default=0)
    timezone: str = field(default="")
    isp: str = field(default="")
    org: str = field(default="")
    query: str = field(default="")

    def __str__(self):
        return (
            "LOCALHOST"
            if self.status == "localhost"
            else "DESCONHECIDO"
            if self.status == "unknown"
            else f"{self.country} | {self.region} | {self.city}"
        )

    @classmethod
    def from_dict(cls, env):
        return cls(
            **{k: v for k, v in env.items() if k in inspect.signature(cls).parameters}
        )

    def to_model(self, pessoa: Pessoa) -> dict:
        return dict(
            pessoa=pessoa,
            ip=self.query,
            pais=self.country,
            estado=self.regionName or self.region,
            cidade=self.city,
        )


def get_external_ip():
    global _external_ip
    if _external_ip[0] < time.time() - 300:
        try:
            public_ip = httpx.get("https://api.ipify.org").text
            _external_ip = (time.time(), public_ip)
            logging.getLogger(__name__).info("Current external IP: %s", public_ip)
        except httpx.RequestError as exc:
            logging.getLogger(__name__).error("Failed to fetch external IP: %s", exc)

    return _external_ip[1]


def get_ip_from_request(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    if ip == "127.0.0.1":
        ip = get_external_ip()
    return ip


def update_location_pessoa(pessoa: Pessoa, location: IPLocation):
    """Atualiza a localização da pessoa, retornando True se houve mudança"""
    if not pessoa:
        return False
    if (
        last_location := PessoaLocalizacao.objects.filter(pessoa=pessoa)
        .order_by("-when")
        .last()
    ):
        if (
            last_location.ip == location.query
            and last_location.pais == location.country
            and last_location.estado == (location.region or location.regionName)
            and last_location.cidade == location.city
        ):
            return False
    _ = PessoaLocalizacao.objects.create(**location.to_model(pessoa))

    logging.getLogger(__name__).info(f"Nova localização para {pessoa} -> {location}")
    return True


class LocationService:
    _external_ip = (0, "")

    def get_external_ip(self):
        if self._external_ip[0] < time.time() - 300:
            try:
                public_ip = httpx.get("https://api.ipify.org").text
                self._external_ip = (time.time(), public_ip)
                logging.getLogger(__name__).info("Current external IP: %s", public_ip)
            except httpx.RequestError as exc:
                logging.getLogger(__name__).error(
                    "Failed to fetch external IP: %s", exc
                )

        return self._external_ip[1]

    def get_ip_from_request(self, request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        if ip == "127.0.0.1":
            ip = LocationService().get_external_ip()
        return ip

    # def get_location_from_ip(self, ip:str)->
