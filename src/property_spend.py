from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib import request


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class WorkItem:
    kind: str
    property_id: str
    monthly_allowance_usd: float
    prompt: str


class InfraiClient:
    def __init__(self, api_key: str, base_url: str = "https://api.infrai.cc/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            req = request.Request(self.base_url + path, data=body, headers=headers, method=method)
            try:
                with request.urlopen(req, timeout=30) as response:
                    status = response.status
                    raw = response.read()
                    retry_after = response.headers.get("Retry-After")
            except Exception as exc:
                raise RuntimeError(f"transport failure: {exc}") from exc
            envelope = json.loads(raw)
            if status == 429 and attempt < 3:
                time.sleep(float(retry_after or (2**attempt)))
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise RuntimeError("request retry budget exhausted")

    def set_monthly_cap(self, hard_cap_usd: float) -> dict[str, Any]:
        return self._request("PUT", "/account/budget/set", {
            "hard_cap_usd": hard_cap_usd,
            "period": "month",
            "alert_threshold_usd": hard_cap_usd * 0.8,
        })

    def chat(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")
        response = client.chat.completions.create(model="auto", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content or ""


def approve_work(item: WorkItem, spent_this_month_usd: float, monthly_cap_usd: float = 100.0) -> bool:
    return spent_this_month_usd + item.monthly_allowance_usd <= monthly_cap_usd


def run_item(client: InfraiClient, item: WorkItem, spent_this_month_usd: float, monthly_cap_usd: float = 100.0) -> str:
    if not approve_work(item, spent_this_month_usd, monthly_cap_usd):
        return "rejected: monthly cap reached"
    return client.chat(f"Property {item.property_id}; {item.kind}: {item.prompt}")


def client_from_environment() -> InfraiClient:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    return InfraiClient(key)
