from __future__ import annotations

import httpx

from .messages import ApiMessage, HealthResponse, MessagesRequest, MessagesResponse


class BankRepClientError(Exception):
    pass


class BankRepClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 120.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http_client = http_client

    def _client_context(self) -> httpx.Client:
        if self._http_client is not None:
            return self._http_client
        return httpx.Client(base_url=self._base_url, timeout=self._timeout)

    def health(self) -> bool:
        try:
            client = self._client_context()
            own_client = self._http_client is None
            try:
                response = client.get("/health")
                response.raise_for_status()
                data = HealthResponse.model_validate(response.json())
                return data.status == "ok"
            finally:
                if own_client:
                    client.close()
        except (httpx.HTTPError, ValueError):
            return False

    def get_messages(self) -> list[ApiMessage]:
        client = self._client_context()
        own_client = self._http_client is None
        try:
            response = client.get("/api/v1/messages")
            response.raise_for_status()
            data = MessagesResponse.model_validate(response.json())
            return data.messages
        finally:
            if own_client:
                client.close()

    def post_messages(self, messages: list[ApiMessage]) -> list[ApiMessage]:
        if not messages:
            raise BankRepClientError("messages must not be empty")
        if messages[-1].role != "user":
            raise BankRepClientError("last message must have role 'user'")

        payload = MessagesRequest(messages=messages)
        client = self._client_context()
        own_client = self._http_client is None
        try:
            response = client.post(
                "/api/v1/messages",
                json=payload.model_dump(),
            )
            if response.status_code >= 400:
                detail = response.text
                try:
                    detail = response.json().get("detail", detail)
                except ValueError:
                    pass
                raise BankRepClientError(f"HTTP {response.status_code}: {detail}")
            data = MessagesResponse.model_validate(response.json())
            return data.messages
        finally:
            if own_client:
                client.close()
