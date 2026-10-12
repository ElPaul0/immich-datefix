"""Filename → capture datetime patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable


@dataclass(frozen=True)
class Pattern:
    id: str
    label: str
    description: str
    example: str
    regex: re.Pattern[str]
    parse: Callable[[re.Match[str], int, int], datetime | None]


def _dt(
    y: int, m: int, d: int, hh: int, mm: int, ss: int = 0
) -> datetime | None:
    try:
        return datetime(y, m, d, hh, mm, ss, tzinfo=timezone.utc)
    except ValueError:
        return None


def _date_only(m: re.Match[str], hour: int, minute: int) -> datetime | None:
    return _dt(int(m["y"]), int(m["mo"]), int(m["d"]), hour, minute, 0)


def _date_time(m: re.Match[str], _h: int, _mi: int) -> datetime | None:
    ss = int(m.groupdict().get("s") or 0)
    return _dt(
        int(m["y"]),
        int(m["mo"]),
        int(m["d"]),
        int(m["h"]),
        int(m["mi"]),
        ss,
    )


def _unix_s(m: re.Match[str], _h: int, _mi: int) -> datetime | None:
    try:
        return datetime.fromtimestamp(int(m["ts"]), tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None


def _unix_ms(m: re.Match[str], _h: int, _mi: int) -> datetime | None:
    try:
        return datetime.fromtimestamp(int(m["ts"]) / 1000.0, tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None


def _dotnet_ticks(m: re.Match[str], _h: int, _mi: int) -> datetime | None:
    """.NET / Facebook-style ticks: 100ns since 0001-01-01 UTC."""
    try:
        ticks = int(m["ticks"])
        # Unix epoch in ticks
        unix_s = (ticks - 621_355_968_000_000_000) / 10_000_000
        if unix_s < 0 or unix_s > 4_102_444_800:  # ~2100
            return None
        return datetime.fromtimestamp(unix_s, tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None


PATTERNS: list[Pattern] = [
    Pattern(
        id="whatsapp",
        label="WhatsApp",
        description="IMG-/VID-YYYYMMDD-WA#### — date souvent = réception",
        example="IMG-20261002-WA0001.jpg",
        regex=re.compile(
            r"^(?:IMG|VID)-(?P<y>\d{4})(?P<mo>\d{2})(?P<d>\d{2})-WA\d+",
            re.IGNORECASE,
        ),
        parse=_date_only,
    ),
    Pattern(
        id="screenshot",
        label="Screenshot",
        description="Screenshot_YYYYMMDD-HHMMSS",
        example="Screenshot_20261002-143015.png",
        regex=re.compile(
            r"^Screenshot[_-](?P<y>\d{4})(?P<mo>\d{2})(?P<d>\d{2})[_-](?P<h>\d{2})(?P<mi>\d{2})(?P<s>\d{2})",
            re.IGNORECASE,
        ),
        parse=_date_time,
    ),
    Pattern(
        id="pixel",
        label="Google Pixel",
        description="PXL_YYYYMMDD_HHMMSS…",
        example="PXL_20261002_143015123.jpg",
        regex=re.compile(
            r"^PXL_(?P<y>\d{4})(?P<mo>\d{2})(?P<d>\d{2})_(?P<h>\d{2})(?P<mi>\d{2})(?P<s>\d{2})",
            re.IGNORECASE,
        ),
        parse=_date_time,
    ),
    Pattern(
        id="img_underscore",
        label="IMG_YYYYMMDD_HHMMSS",
        description="Classique appareil / export",
        example="IMG_20261002_143015.jpg",
        regex=re.compile(
            r"^IMG_(?P<y>\d{4})(?P<mo>\d{2})(?P<d>\d{2})_(?P<h>\d{2})(?P<mi>\d{2})(?P<s>\d{2})",
            re.IGNORECASE,
        ),
        parse=_date_time,
    ),
    Pattern(
        id="yyyymmdd_hhmmss",
        label="YYYYMMDD_HHMMSS",
        description="Préfixe date-heure compact",
        example="20261002_143015.jpg",
        regex=re.compile(
            r"^(?P<y>\d{4})(?P<mo>\d{2})(?P<d>\d{2})[_-](?P<h>\d{2})(?P<mi>\d{2})(?P<s>\d{2})\b"
        ),
        parse=_date_time,
    ),
    Pattern(
        id="iso_filename",
        label="YYYY-MM-DD_HH-MM-SS",
        description="ISO-ish dans le nom",
        example="2026-10-02_14-30-15.jpg",
        regex=re.compile(
            r"(?P<y>\d{4})-(?P<mo>\d{2})-(?P<d>\d{2})[ _](?P<h>\d{2})-(?P<mi>\d{2})-(?P<s>\d{2})"
        ),
        parse=_date_time,
    ),
    Pattern(
        id="unix_ms",
        label="Timestamp Unix (ms)",
        description="13 chiffres (epoch millisecondes)",
        example="1727872215123.jpg",
        regex=re.compile(r"^(?P<ts>1[6-9]\d{11})\b"),
        parse=_unix_ms,
    ),
    Pattern(
        id="unix_s",
        label="Timestamp Unix (s)",
        description="10 chiffres (epoch secondes)",
        example="1727872215.jpg",
        regex=re.compile(r"^(?P<ts>1[6-9]\d{8})\b"),
        parse=_unix_s,
    ),
    Pattern(
        id="dotnet_ticks",
        label="Ticks (.NET / Facebook-like)",
        description="~18 chiffres (ticks 100ns depuis year 1)",
        example="638639184000000000.jpg",
        regex=re.compile(r"(?P<ticks>63\d{16})\b"),
        parse=_dotnet_ticks,
    ),
]

PATTERN_BY_ID = {p.id: p for p in PATTERNS}


def match_filename(
    filename: str, hour: int = 12, minute: int = 0
) -> tuple[Pattern, datetime] | None:
    name = filename.rsplit("/", 1)[-1]
    stem = name
    for pat in PATTERNS:
        m = pat.regex.search(stem)
        if not m:
            continue
        dt = pat.parse(m, hour, minute)
        if dt is None:
            continue
        # Garde-fou années raisonnables
        if dt.year < 1995 or dt.year > 2100:
            continue
        return pat, dt
    return None
