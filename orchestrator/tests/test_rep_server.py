from unittest.mock import MagicMock, patch

import httpx
import pytest

from orchestrator.rep_server import RepServer, start_rep_server, wait_for_health


def test_wait_for_health_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}

    with patch("orchestrator.rep_server.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.get.return_value = mock_response
        assert wait_for_health("http://127.0.0.1:8000", timeout=1.0) is True


def test_wait_for_health_timeout():
    with patch("orchestrator.rep_server.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.get.side_effect = httpx.ConnectError("down")
        assert wait_for_health("http://127.0.0.1:8000", timeout=0.3) is False


def test_rep_server_stop_terminates_process():
    proc = MagicMock()
    proc.poll.return_value = None
    proc.wait.return_value = 0
    server = RepServer(process=proc, base_url="http://127.0.0.1:8000")
    server.stop()
    proc.send_signal.assert_called_once()
    proc.wait.assert_called()


def test_start_rep_server_unhealthy_stops_process():
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None

    with (
        patch("orchestrator.rep_server.subprocess.Popen", return_value=mock_proc),
        patch("orchestrator.rep_server.wait_for_health", return_value=False),
        patch("orchestrator.rep_server.get_bank_rep_dir"),
        patch("orchestrator.rep_server.get_bank_rep_base_url", return_value="http://127.0.0.1:8000"),
    ):
        with pytest.raises(RuntimeError, match="did not become healthy"):
            start_rep_server()
        mock_proc.send_signal.assert_called()
