import base64
import pickle
from typing import Any
from urllib.parse import urlencode

from django.http import HttpRequest, HttpResponseRedirect


class HttpEncryptedRedirectResponse(HttpResponseRedirect):
    KEY = "xpto"

    def __init__(
        self,
        redirect_to: str,
        data: dict | None = None,
        use_query: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        encrypted_data = self.encrypt_dict(data)
        if data and use_query:
            redirect_to += ("?" if "?" not in redirect_to else "&") + urlencode(
                {self.KEY: encrypted_data}
            )
        else:
            headers = kwargs.setdefault("headers", {})
            headers[self.KEY] = encrypted_data
            kwargs["headers"] = headers
        super().__init__(redirect_to, *args, **kwargs)
        # if data and not use_query:
        #     encrypted_data = self.encrypt_dict(data)
        #     self.set_data(encrypted_data, use_query)

    def set_data(self, encrypted_data: dict, use_query: bool):
        if use_query:
            self._set_data_query(encrypted_data)
        else:
            self._set_data_header(encrypted_data)

    def _set_data_query(self, encrypted_data):
        self.url += ("?" if "?" not in self.url else "&") + urlencode(
            {self.KEY: encrypted_data}
        )

    def _set_data_header(self, encrypted_data):
        self.headers[self.KEY] = encrypted_data

    @classmethod
    def encrypt_dict(cls, data) -> str:
        return base64.b64encode(pickle.dumps(data)).decode()

    @classmethod
    def decrypt_dict(cls, encrypted_data: str) -> Any:
        return pickle.loads(base64.b64decode(encrypted_data))

    @classmethod
    def get_data(cls, request: HttpRequest) -> dict | None:
        if encrypted_data := (request.headers.get(cls.KEY) or request.GET.get(cls.KEY)):
            return cls.decrypt_dict(encrypted_data)
        return None
