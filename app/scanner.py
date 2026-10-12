"""Scan Immich library and build correction candidates."""

from __future__ import annotations

from datetime import datetime, timezone
from collections.abc import Callable
from typing import Any

from app.config import Settings
from app.immich import ImmichClient
from app.patterns import PATTERNS, match_filename


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def asset_current_date(asset: dict[str, Any]) -> datetime | None:
    exif = asset.get("exifInfo") or {}
    for key in (
        exif.get("dateTimeOriginal"),
        asset.get("localDateTime"),
        asset.get("fileCreatedAt"),
        asset.get("createdAt"),
    ):
        dt = _parse_iso(key if isinstance(key, str) else None)
        if dt:
            return dt
    return None


def asset_filename(asset: dict[str, Any]) -> str:
    return (
        asset.get("originalFileName")
        or asset.get("originalPath")
        or asset.get("fileName")
        or ""
    ).rsplit("/", 1)[-1]


def scan_library(
    client: ImmichClient,
    settings: Settings,
    *,
    progress: Callable[[int], None] | None = None,
) -> dict[str, Any]:
    pattern_stats: dict[str, dict[str, Any]] = {
        p.id: {
            "id": p.id,
            "label": p.label,
            "description": p.description,
            "example": p.example,
            "matched": 0,
            "needs_fix": 0,
            "samples": [],
        }
        for p in PATTERNS
    }
    candidates: list[dict[str, Any]] = []
    scanned = 0
    matched_any = 0

    for asset in client.iter_assets(settings.page_size):
        scanned += 1
        if progress and scanned % 200 == 0:
            progress(scanned)

        fname = asset_filename(asset)
        if not fname:
            continue
        hit = match_filename(fname, settings.default_hour, settings.default_minute)
        if not hit:
            continue
        pat, name_dt = hit
        matched_any += 1
        st = pattern_stats[pat.id]
        st["matched"] += 1

        current = asset_current_date(asset)
        delta = None
        needs = False
        if current is None:
            needs = True
            delta = None
        else:
            delta = abs((current - name_dt).total_seconds())
            needs = delta >= settings.min_delta_seconds

        if needs:
            st["needs_fix"] += 1
            item = {
                "id": asset.get("id"),
                "filename": fname,
                "pattern_id": pat.id,
                "pattern_label": pat.label,
                "name_date": name_dt.isoformat().replace("+00:00", "Z"),
                "current_date": current.isoformat().replace("+00:00", "Z") if current else None,
                "delta_seconds": int(delta) if delta is not None else None,
            }
            candidates.append(item)
            if len(st["samples"]) < 5:
                st["samples"].append(item)

    return {
        "scanned": scanned,
        "matched_any": matched_any,
        "needs_fix": len(candidates),
        "patterns": list(pattern_stats.values()),
        "candidates": candidates,
        "min_delta_seconds": settings.min_delta_seconds,
    }


def apply_fixes(
    client: ImmichClient,
    candidates: list[dict[str, Any]],
    pattern_ids: set[str],
    *,
    dry_run: bool = True,
    batch_size: int = 50,
    progress: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    selected = [c for c in candidates if c.get("pattern_id") in pattern_ids and c.get("id")]
    total = len(selected)
    # Group by target date ISO for bulk updates
    by_date: dict[str, list[str]] = {}
    for c in selected:
        by_date.setdefault(c["name_date"], []).append(c["id"])

    updated = 0
    processed = 0
    errors: list[str] = []
    if progress:
        progress(0, total)

    if not dry_run:
        for date_iso, ids in by_date.items():
            for i in range(0, len(ids), batch_size):
                chunk = ids[i : i + batch_size]
                try:
                    client.update_dates(chunk, date_iso)
                    updated += len(chunk)
                except Exception as e:
                    errors.append(f"{date_iso}: {e}")
                processed += len(chunk)
                if progress:
                    progress(min(processed, total), total)
    else:
        updated = total
        processed = total
        if progress:
            progress(total, total)

    return {
        "dry_run": dry_run,
        "selected": total,
        "updated": updated,
        "errors": errors,
        "by_pattern": {
            pid: sum(1 for c in selected if c["pattern_id"] == pid)
            for pid in pattern_ids
        },
    }


def patterns_catalog() -> list[dict[str, str]]:
    return [
        {
            "id": p.id,
            "label": p.label,
            "description": p.description,
            "example": p.example,
        }
        for p in PATTERNS
    ]
