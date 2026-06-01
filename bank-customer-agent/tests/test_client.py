import httpx
import pytest

from bank_customer.client import BankRepClient, BankRepClientError
from bank_customer.messages import ApiMessage


GREETING = ApiMessage(role="assistant", content="Hello! Please provide your Customer ID?")


def _make_client(handler) -> BankRepClient:
    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport, base_url="http://test")
    return BankRepClient("http://test", http_client=http)


def test_health_ok():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "ok"})

    assert _make_client(handler).health() is True


def test_health_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    assert _make_client(handler).health() is False


def test_get_messages():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"messages": [{"role": "assistant", "content": "Hi"}]},
        )

    messages = _make_client(handler).get_messages()
    assert len(messages) == 1
    assert messages[0].content == "Hi"


def test_post_messages():
    def handler(request: httpx.Request) -> httpx.Response:
        body = request.read().decode()
        assert '"role":"user"' in body or '"role": "user"' in body
        return httpx.Response(
            200,
            json={
                "messages": [
                    {"role": "assistant", "content": "Hi"},
                    {"role": "user", "content": "CUST-1001"},
                    {"role": "assistant", "content": "Hello Alice"},
                ]
            },
        )

    client = _make_client(handler)
    result = client.post_messages(
        [
            GREETING,
            ApiMessage(role="user", content="CUST-1001"),
        ]
    )
    assert result[-1].content == "Hello Alice"


def test_post_requires_user_last():
    client = _make_client(lambda r: httpx.Response(200, json={"messages": []}))
    with pytest.raises(BankRepClientError, match="last message"):
        client.post_messages([GREETING])
