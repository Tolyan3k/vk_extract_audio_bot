import hashlib
import multiprocessing
import secrets
import string
import time
import urllib
from typing import (
    ClassVar,
    ParamSpecKwargs,
)

import requests

from vk_extract_audio_bot.errors import (
    VkExtractAudioBotError,
)


RPS = 5
RPS_DELAY = 1 / RPS


class LastRpsRequests:

    def __init__(self, rps: int) -> None:
        self.rps = rps
        self.request_times = []
        self.full = False

    def request(self) -> None:
        if self.full:
            current_time = time.time()
            least_rps_request_time = sorted(self.request_times).pop()
            time_diff = current_time - least_rps_request_time
            time.sleep(max(0.0, 1.0 - time_diff))
            self.request_times = []
            self.full = False
        self.request_times += [time.time()]
        if self.rps <= len(self.request_times):
            self.full = True

    def get_delay(self) -> float:
        self.request()
        return 0.0

    def timestamp(self) -> None:
        ...


class VkAndroidApi:
    """https://habr.com/ru/articles/519302/"""

    # pylint: disable=R0903
    session: ClassVar[requests.Session] = requests.Session()
    # ruff: noqa: RUF012
    session.headers = {
        "User-Agent":
            ("VKAndroidApp/4.13.1-1206 (Android 4.4.3; SDK 19; armeabi; ; ru)"),
        "Accept": "image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, */*",
    }

    def _get_auth_params(self, login: str, password: str) -> dict:
        return {
            "grant_type": "password",
            "scope": "nohttps,audio",
            "client_id": 2274003,
            "client_secret": "hHbZxrka2uZ6jB1inYsH",
            "validate_token": "true",
            "username": login,
            "password": password,
        }

    # pylint: disable=too-many-arguments
    # ruff: noqa: PLR0913
    def __init__(
        self,
        login: str | None = None,
        password: str | None = None,
        token: str | None = None,
        secret: str | None = None,
        v: float = 5.95,
    ) -> None:
        self.v = v
        self.lock = multiprocessing.Lock()
        self.last_rps_requests = LastRpsRequests(RPS)

        # Генерируем рандомный device_id
        self.device_id = "".join(
            secrets.choice(string.ascii_lowercase + string.digits)
            for i in range(16)
        )
        if token is not None and secret is not None:
            self.token = token
            self.secret = secret
        else:
            answer = self.session.get(
                "https://oauth.vk.com/token",
                params=self._get_auth_params(login, password),
            ).json()
            if "error" in answer:
                msg = "invalid login|password!"
                raise PermissionError(msg)
            self.secret = answer["secret"]
            self.token = answer["access_token"]

        # Методы, "Открывающие" доступ к аудио. Без них, аудио получить не получится
        # pylint: disable=expression-not-assigned
        self.method("execute.getUserInfo", func_v=9)
        # pylint: disable=expression-not-assigned
        self.method("auth.refreshToken", lang="ru")

    def method(
        self,
        method: str,
        **params: ParamSpecKwargs,
    ) -> dict:
        url = (
            f"/method/{method}?v={self.v}&access_token={self.token}&device_id={self.device_id}"
            + "".join(
                f"&{i}={param}" for i, param in params.items()
                if param is not None
            )
        )
        # генерация ссылки по которой будет генерироваться md5-подпись
        # обратите внимание - в даннаой ссылке нет urlencode параметров
        return self._send(url, params, method)

    def _send(
        self,
        url: str,
        params: dict | None = None,
        method: str | None = None,
        headers: dict | None = None,
    ) -> dict:
        # ruff: noqa: S324
        req_hash = hashlib.md5((url + self.secret).encode()).hexdigest()

        if method is not None and params is not None:
            token = self.token
            device_id = self.device_id
            v = self.v
            url = f"/method/{method}?v={v}&access_token={token}&device_id={device_id}"
            url += "".join(
                "&" + i + "=" + urllib.parse.quote_plus(str(params[i]))
                for i in params
                if (params[i] is not None)
            )

        response: dict = None
        with self.lock:
            self.last_rps_requests.request()
            if headers is None:
                response = self.session.get(
                    "https://api.vk.com" + url + "&sig=" + req_hash,
                ).json()
            else:
                response = self.session.get(
                    "https://api.vk.com" + url + "&sig=" + req_hash,
                    headers=headers,
                ).json()

        if response.get("error"):
            raise VkExtractAudioBotError(response.get("error"))

        return response
