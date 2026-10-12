"""Minimal Immich API client (v3-compatible)."""

from __future__ import annotations

from typing import Any

import httpx


class ImmichError(RuntimeError):
    pass


class ImmichClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key.strip()
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "x-api-key": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def _check(self, res: httpx.Response) -> Any:
        if res.status_code >= 400:
            detail = res.text[:500]
            try:
                detail = res.json()
            except Exception:
                pass
            raise ImmichError(f"Immich {res.status_code}: {detail}")
        if res.status_code == 204 or not res.content:
            return None
        return res.json()

    def ping(self) -> dict[str, Any]:
        return self._check(self._client.get("/api/server/version"))

    def iter_assets(self, page_size: int = 500):
        """Yield asset dicts via search/metadata pagination."""
        page = 1
        while True:
            body: dict[str, Any] = {
                "page": page,
                "size": page_size,
                "withExif": True,
            }
            data = self._check(self._client.post("/api/search/metadata", json=body))
            assets = []
            if isinstance(data, dict):
                assets = data.get("assets", {}).get("items") or data.get("items") or []
                # Some versions nest differently
                if not assets and "assets" in data and isinstance(data["assets"], list):
                    assets = data["assets"]
            elif isinstance(data, list):
                assets = data

            if not assets:
                break
            for a in assets:
                yield a
            if len(assets) < page_size:
                break
            page += 1
            if page > 10_000:
                break

    def update_dates(self, ids: list[str], date_iso: str) -> Any:
        """Bulk update dateTimeOriginal for asset ids."""
        # Immich AssetBulkUpdateDto
        payload = {"ids": ids, "dateTimeOriginal": date_iso}
        return self._check(self._client.put("/api/assets", json=payload))
