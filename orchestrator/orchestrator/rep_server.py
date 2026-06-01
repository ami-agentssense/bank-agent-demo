from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass

import httpx

from .config import (
    get_bank_rep_base_url,
    get_bank_rep_dir,
    get_rep_startup_timeout,
)


@dataclass
class RepServer:
    process: subprocess.Popen[bytes]
    base_url: str

    def stop(self) -> None:
        if self.process.poll() is not None:
            return
        self.process.send_signal(signal.SIGTERM)
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)


def wait_for_health(base_url: str, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    url = f"{base_url.rstrip('/')}/health"
    while time.monotonic() < deadline:
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(url)
                if response.status_code == 200 and response.json().get("status") == "ok":
                    return True
        except (httpx.HTTPError, ValueError):
            pass
        time.sleep(0.25)
    return False


def start_rep_server() -> RepServer:
    base_url = get_bank_rep_base_url()
    rep_dir = get_bank_rep_dir()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(rep_dir)

    process = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "bank_demo.api:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=str(rep_dir),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    server = RepServer(process=process, base_url=base_url)
    if not wait_for_health(base_url, get_rep_startup_timeout()):
        server.stop()
        raise RuntimeError(f"bank rep did not become healthy at {base_url}")
    return server
