"""Small JSON-over-HTTPS transport with sanitized provider failures."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from .base import ConnectorError


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    payload: Mapping[str, Any]
    headers: Mapping[str, str]


class HttpTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        query: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> HttpResponse: ...


class UrllibJsonTransport:
    """Production transport. Provider bodies are never included in exceptions."""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        query: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> HttpResponse:
        if not url.startswith("https://"):
            raise ConnectorError("unsafe_transport", "Connector transport requires HTTPS")
        query_values = {key: str(value) for key, value in (query or {}).items() if value is not None}
        request_url = url
        if query_values:
            request_url += ("&" if "?" in url else "?") + urllib.parse.urlencode(query_values)
        body = None if json_body is None else json.dumps(json_body).encode("utf-8")
        request_headers = {"Accept": "application/json", **dict(headers or {})}
        if body is not None:
            request_headers["Content-Type"] = "application/json"
        request = urllib.request.Request(request_url, data=body, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ConnectorError("invalid_provider_response", "Provider response must be an object")
                safe_headers = {
                    name: response.headers[name]
                    for name in ("Retry-After", "Content-Type")
                    if response.headers.get(name)
                }
                return HttpResponse(response.status, payload, safe_headers)
        except urllib.error.HTTPError as exc:
            raise _http_error(exc.code, exc.headers.get("Retry-After")) from None
        except urllib.error.URLError:
            raise ConnectorError("provider_unavailable", "Provider request could not be completed", retryable=True) from None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ConnectorError("invalid_provider_response", "Provider returned invalid JSON") from None


class FixtureTransport:
    """Deterministic queued responses for tests and the mock-only CLI command."""

    def __init__(self, responses: Sequence[HttpResponse | Mapping[str, Any]]) -> None:
        self._responses = deque(
            response if isinstance(response, HttpResponse) else HttpResponse(200, response, {})
            for response in responses
        )
        self.requests: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        query: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> HttpResponse:
        self.requests.append(
            {
                "method": method,
                "url": url,
                "header_names": sorted((headers or {}).keys()),
                "query_names": sorted((query or {}).keys()),
                "json_body": json.loads(json.dumps(json_body)) if json_body else None,
                "timeout": timeout,
            }
        )
        if not self._responses:
            raise ConnectorError("fixture_exhausted", "No mocked provider response remains")
        response = self._responses.popleft()
        if response.status >= 400:
            raise _http_error(response.status, response.headers.get("Retry-After"))
        return response


def _http_error(status: int, retry_after: str | None = None) -> ConnectorError:
    if status in (401, 403):
        return ConnectorError("authorization_rejected", "Provider rejected read-only authorization")
    if status == 404:
        return ConnectorError("data_unavailable", "Provider has no record for the authorized resource")
    if status == 429:
        details = {"retry_after": retry_after} if retry_after else {}
        return ConnectorError("rate_or_quota_limit", "Provider rate or quota limit reached", retryable=True, details=details)
    if 500 <= status <= 599:
        return ConnectorError("provider_unavailable", "Provider service is temporarily unavailable", retryable=True)
    return ConnectorError("provider_request_rejected", f"Provider rejected the request with HTTP {status}")
