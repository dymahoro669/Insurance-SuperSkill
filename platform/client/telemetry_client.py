"""
Telemetry Client Library for Insurance-SuperSkill Platform

Provides sync/async event reporting with retry, exponential backoff,
and local disk buffering for offline resilience.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


DEFAULT_PLATFORM_URL = "http://127.0.0.1:8080"
MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds
BUFFER_DIR_NAME = ".telemetry_buffer"


class TelemetryClient:
    """Client for reporting telemetry events to the Insurance-SuperSkill Platform."""

    def __init__(
        self,
        platform_url: str = DEFAULT_PLATFORM_URL,
        api_key: Optional[str] = None,
    ):
        self.platform_url = platform_url.rstrip("/")
        self.api_key = api_key
        self._session = requests.Session()
        if api_key:
            self._session.headers["X-API-Key"] = api_key

        self._buffer_dir = Path.home() / BUFFER_DIR_NAME
        self._buffer_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def report_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Report a telemetry event synchronously.

        Args:
            event_data: Dictionary containing event fields.  If ``event_id`` is
                omitted a UUID will be generated automatically.

        Returns:
            The JSON response from the platform, or an error dict on failure.
        """
        payload = self._normalize_payload(event_data)
        return self._post_with_retry("/api/v1/telemetry/events", payload)

    def report_event_async(self, event_data: Dict[str, Any]) -> asyncio.Future:
        """Report a telemetry event asynchronously (returns an asyncio Future)."""
        payload = self._normalize_payload(event_data)
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, self._post_with_retry, "/api/v1/telemetry/events", payload)

    def report_l1_score(self, event_id: str, score: int, verdict: str) -> Dict[str, Any]:
        """Update the L1 score for an existing event.

        The platform stores L1 scores inline with the invocation event; this
        helper constructs a minimal payload and reports it.  If the event does
        not yet exist it will be created with default values.
        """
        payload = {
            "event_id": event_id,
            "session_id": event_id,
            "trace_id": event_id,
            "user_input": "",
            "primary_skill": "unknown",
            "confidence": 0.0,
            "route_chain": [],
            "duration_ms": 0,
            "tokens_used": 0,
            "model": "",
            "l1_score": score,
            "l1_verdict": verdict,
            "output_length": 0,
            "output_format": "markdown",
            "failed_dimensions": [],
        }
        return self.report_event(payload)

    def flush_buffer(self) -> Dict[str, Any]:
        """Attempt to re-send all locally buffered events.

        Returns:
            A summary dict with ``sent``, ``failed``, and ``remaining`` counts.
        """
        files = sorted(self._buffer_dir.glob("*.json"))
        sent = 0
        failed = 0
        for path in files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                path.unlink(missing_ok=True)
                continue

            resp = self._post_with_retry("/api/v1/telemetry/events", payload, buffer_on_fail=False)
            if resp.get("status") == "ok":
                path.unlink(missing_ok=True)
                sent += 1
            else:
                failed += 1

        remaining = len(list(self._buffer_dir.glob("*.json")))
        return {"sent": sent, "failed": failed, "remaining": remaining}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalize_payload(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure required fields exist and add auto-collected metadata."""
        payload = dict(event_data)
        if "event_id" not in payload or not payload["event_id"]:
            payload["event_id"] = str(uuid.uuid4())

        # Auto-collect / infer missing fields when possible
        payload.setdefault("session_id", payload["event_id"])
        payload.setdefault("trace_id", payload["event_id"])
        payload.setdefault("route_chain", [])
        payload.setdefault("cross_skill_invoked", False)
        payload.setdefault("output_format", "markdown")
        payload.setdefault("has_pii", False)
        payload.setdefault("failed_dimensions", [])
        payload.setdefault("l2_triggered", False)
        payload.setdefault("l3_triggered", False)
        return payload

    def _post_with_retry(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        buffer_on_fail: bool = True,
    ) -> Dict[str, Any]:
        url = self.platform_url + endpoint
        last_exception: Optional[Exception] = None

        for attempt in range(MAX_RETRIES):
            try:
                resp = self._session.post(url, json=payload, timeout=30)
                if resp.status_code == 200:
                    return resp.json()
                # Non-2xx that isn't a transient network error – still retry once
                if attempt == MAX_RETRIES - 1:
                    return {"status": "error", "code": resp.status_code, "detail": resp.text}
            except requests.RequestException as exc:
                last_exception = exc
                wait = BACKOFF_BASE * (2 ** attempt)
                time.sleep(wait)

        # All retries exhausted
        if buffer_on_fail:
            self._buffer_event(payload)
            return {
                "status": "buffered",
                "message": "Network unavailable; event saved to local buffer.",
                "error": str(last_exception),
            }
        return {"status": "error", "message": str(last_exception)}

    def _buffer_event(self, payload: Dict[str, Any]) -> None:
        ts = time.time()
        fname = f"{ts}_{payload.get('event_id', uuid.uuid4())}.json"
        path = self._buffer_dir / fname
        try:
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()


# ------------------------------------------------------------------------------
# Async-first wrapper for pure asyncio codebases
# ------------------------------------------------------------------------------

class AsyncTelemetryClient:
    """Async-native telemetry client using ``aiohttp`` when available,
    falling back to thread-pool executor otherwise."""

    def __init__(
        self,
        platform_url: str = DEFAULT_PLATFORM_URL,
        api_key: Optional[str] = None,
    ):
        self.platform_url = platform_url.rstrip("/")
        self.api_key = api_key
        self._buffer_dir = Path.home() / BUFFER_DIR_NAME
        self._buffer_dir.mkdir(parents=True, exist_ok=True)
        self._session: Any = None

    async def _get_session(self):
        if self._session is None:
            try:
                import aiohttp
                connector = aiohttp.TCPConnector(limit=10)
                headers = {"X-API-Key": self.api_key} if self.api_key else {}
                self._session = aiohttp.ClientSession(connector=connector, headers=headers)
            except ImportError:
                self._session = False  # type: ignore[assignment]
        return self._session

    async def report_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._normalize_payload(event_data)
        session = await self._get_session()
        if session is False:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._sync_post, payload)
        return await self._aio_post("/api/v1/telemetry/events", payload)

    async def report_l1_score(self, event_id: str, score: int, verdict: str) -> Dict[str, Any]:
        payload = {
            "event_id": event_id,
            "session_id": event_id,
            "trace_id": event_id,
            "user_input": "",
            "primary_skill": "unknown",
            "confidence": 0.0,
            "route_chain": [],
            "duration_ms": 0,
            "tokens_used": 0,
            "model": "",
            "l1_score": score,
            "l1_verdict": verdict,
            "output_length": 0,
            "output_format": "markdown",
            "failed_dimensions": [],
        }
        return await self.report_event(payload)

    async def flush_buffer(self) -> Dict[str, Any]:
        files = sorted(self._buffer_dir.glob("*.json"))
        sent = 0
        failed = 0
        for path in files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                path.unlink(missing_ok=True)
                continue
            resp = await self._aio_post("/api/v1/telemetry/events", payload, buffer_on_fail=False)
            if resp.get("status") == "ok":
                path.unlink(missing_ok=True)
                sent += 1
            else:
                failed += 1
        remaining = len(list(self._buffer_dir.glob("*.json")))
        return {"sent": sent, "failed": failed, "remaining": remaining}

    # -- helpers -------------------------------------------------------

    def _normalize_payload(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(event_data)
        if "event_id" not in payload or not payload["event_id"]:
            payload["event_id"] = str(uuid.uuid4())
        payload.setdefault("session_id", payload["event_id"])
        payload.setdefault("trace_id", payload["event_id"])
        payload.setdefault("route_chain", [])
        payload.setdefault("cross_skill_invoked", False)
        payload.setdefault("output_format", "markdown")
        payload.setdefault("has_pii", False)
        payload.setdefault("failed_dimensions", [])
        payload.setdefault("l2_triggered", False)
        payload.setdefault("l3_triggered", False)
        return payload

    def _sync_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        client = TelemetryClient(self.platform_url, self.api_key)
        return client._post_with_retry("/api/v1/telemetry/events", payload)

    async def _aio_post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        buffer_on_fail: bool = True,
    ) -> Dict[str, Any]:
        import aiohttp

        url = self.platform_url + endpoint
        last_exception: Optional[Exception] = None

        for attempt in range(MAX_RETRIES):
            try:
                async with self._session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    if attempt == MAX_RETRIES - 1:
                        text = await resp.text()
                        return {"status": "error", "code": resp.status, "detail": text}
            except aiohttp.ClientError as exc:
                last_exception = exc
                wait = BACKOFF_BASE * (2 ** attempt)
                await asyncio.sleep(wait)

        if buffer_on_fail:
            self._buffer_event(payload)
            return {
                "status": "buffered",
                "message": "Network unavailable; event saved to local buffer.",
                "error": str(last_exception),
            }
        return {"status": "error", "message": str(last_exception)}

    def _buffer_event(self, payload: Dict[str, Any]) -> None:
        ts = time.time()
        fname = f"{ts}_{payload.get('event_id', uuid.uuid4())}.json"
        path = self._buffer_dir / fname
        try:
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    async def close(self):
        if self._session and self._session is not False:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
