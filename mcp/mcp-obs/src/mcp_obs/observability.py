"""HTTP client for VictoriaLogs and VictoriaTraces APIs."""

from __future__ import annotations

import json

import httpx


class ObservabilityClient:
    """Thin HTTP client for VictoriaLogs and VictoriaTraces."""

    def __init__(self, victorialogs_url: str, victoriatraces_url: str) -> None:
        self.logs_base = victorialogs_url.rstrip("/")
        self.traces_base = victoriatraces_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "ObservabilityClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    # ── VictoriaLogs ──────────────────────────────────────────────

    async def search_logs(self, query: str, limit: int = 50) -> list[dict]:
        """Search VictoriaLogs using LogsQL."""
        params = {"query": query, "limit": limit}
        resp = await self._http.get(
            f"{self.logs_base}/select/logsql/query",
            params=params,
        )
        resp.raise_for_status()
        # VictoriaLogs returns newline-delimited JSON objects.
        lines = resp.text.strip().splitlines()
        results: list[dict] = []
        for line in lines:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except Exception:
                    results.append({"_raw": line})
        return results

    async def count_errors(self, service: str | None = None, minutes: int = 60) -> list[dict]:
        """Count ERROR-level logs per service over the last N minutes."""
        time_filter = f"_time:{minutes}m"
        parts = [time_filter, "severity:ERROR"]
        if service:
            parts.append(f'service.name:"{service}"')
        query = " ".join(parts)
        resp = await self._http.get(
            f"{self.logs_base}/select/logsql/query",
            params={"query": query, "limit": 1000},
        )
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        # Group by service.name and count.
        counts: dict[str, int] = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                svc = entry.get("service.name", "unknown")
                counts[svc] = counts.get(svc, 0) + 1
            except Exception:
                counts["unknown"] = counts.get("unknown", 0) + 1
        return [{"service": svc, "error_count": cnt} for svc, cnt in counts.items()]

    # ── VictoriaTraces (Jaeger-compatible API) ────────────────────

    async def list_traces(self, service: str, limit: int = 20) -> list[dict]:
        """List recent traces for a service."""
        resp = await self._http.get(
            f"{self.traces_base}/select/jaeger/api/traces",
            params={"service": service, "limit": limit},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    async def get_trace(self, trace_id: str) -> dict | None:
        """Fetch a single trace by ID."""
        resp = await self._http.get(
            f"{self.traces_base}/select/jaeger/api/traces/{trace_id}",
        )
        resp.raise_for_status()
        data = resp.json()
        traces = data.get("data", [])
        return traces[0] if traces else None
