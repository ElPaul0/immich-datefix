from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import get_settings
from app.immich import ImmichClient, ImmichError
from app.scanner import apply_fixes, patterns_catalog, scan_library

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
settings = get_settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = settings.data_dir / "config.json"

app = FastAPI(title="immich-datefix", version="0.2.0")

_lock = threading.Lock()
_job: dict[str, Any] = {
    "kind": None,  # scan | apply
    "state": "idle",  # idle | running | done | error
    "message": "",
    "done": 0,
    "total": 0,
    "error": None,
    "result": None,
}
_last_scan: dict[str, Any] | None = None


def _load_cfg() -> dict[str, str]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_cfg(cfg: dict[str, str]) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def _resolved() -> tuple[str, str]:
    cfg = _load_cfg()
    url = (cfg.get("immich_url") or settings.immich_url).rstrip("/")
    key = cfg.get("immich_api_key") or settings.immich_api_key
    return url, key


def _client() -> ImmichClient:
    url, key = _resolved()
    if not key:
        raise HTTPException(400, "API key Immich manquante (réglages)")
    return ImmichClient(url, key)


def _job_snapshot() -> dict[str, Any]:
    with _lock:
        done = int(_job["done"] or 0)
        total = int(_job["total"] or 0)
        pct = int(round(100 * done / total)) if total > 0 else 0
        if _job["state"] == "done":
            pct = 100
        return {
            "kind": _job["kind"],
            "state": _job["state"],
            "message": _job["message"],
            "done": done,
            "total": total,
            "percent": pct,
            "error": _job["error"],
            "result": _job["result"],
            "has_result": _last_scan is not None,
            "summary": None
            if not _last_scan
            else {
                "scanned": _last_scan["scanned"],
                "matched_any": _last_scan["matched_any"],
                "needs_fix": _last_scan["needs_fix"],
                "patterns": [
                    {
                        "id": p["id"],
                        "label": p["label"],
                        "description": p["description"],
                        "example": p["example"],
                        "matched": p["matched"],
                        "needs_fix": p["needs_fix"],
                        "samples": p["samples"],
                    }
                    for p in _last_scan["patterns"]
                    if p["matched"] > 0
                ],
            },
            # compat ancien champ
            "scanned": done if _job["kind"] == "scan" else _last_scan["scanned"] if _last_scan else 0,
        }


class SettingsBody(BaseModel):
    immich_url: str | None = None
    immich_api_key: str | None = None


class ApplyBody(BaseModel):
    pattern_ids: list[str] = Field(default_factory=list)
    dry_run: bool = True


@app.get("/api/health")
def health():
    return {"ok": True, "version": "0.2.0"}


@app.get("/api/patterns")
def api_patterns():
    return {"patterns": patterns_catalog()}


@app.get("/api/settings")
def get_settings_api():
    url, key = _resolved()
    return {
        "immich_url": url,
        "has_api_key": bool(key),
        "api_key_hint": (key[:4] + "…" + key[-4:]) if key and len(key) > 10 else "",
        "min_delta_seconds": settings.min_delta_seconds,
        "default_hour": settings.default_hour,
    }


@app.post("/api/settings")
def set_settings_api(body: SettingsBody):
    cfg = _load_cfg()
    if body.immich_url is not None:
        cfg["immich_url"] = body.immich_url.strip().rstrip("/")
    if body.immich_api_key is not None and body.immich_api_key.strip():
        cfg["immich_api_key"] = body.immich_api_key.strip()
    _save_cfg(cfg)
    return get_settings_api()


@app.post("/api/ping")
def ping():
    try:
        client = _client()
        ver = client.ping()
        client.close()
        return {"ok": True, "version": ver}
    except ImmichError as e:
        raise HTTPException(502, str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, str(e)) from e


@app.get("/api/job")
@app.get("/api/scan/status")
def job_status():
    return _job_snapshot()


def _run_scan() -> None:
    global _last_scan
    client = None
    try:
        client = _client()
        with _lock:
            _job["message"] = "Scan Immich…"
            _job["done"] = 0
            _job["total"] = 0

        def prog(n: int) -> None:
            with _lock:
                _job["done"] = n
                # total inconnu pendant le scan → barre indéterminée côté UI si total=0
                _job["message"] = f"Scan… {n} assets"

        result = scan_library(client, settings, progress=prog)
        with _lock:
            _last_scan = result
            _job["state"] = "done"
            _job["done"] = result["scanned"]
            _job["total"] = result["scanned"]
            _job["message"] = (
                f"Terminé — {result['scanned']} scannés, "
                f"{result['needs_fix']} à corriger"
            )
            _job["error"] = None
            _job["result"] = {
                "scanned": result["scanned"],
                "needs_fix": result["needs_fix"],
            }
    except Exception as e:
        with _lock:
            _job["state"] = "error"
            _job["error"] = str(e)
            _job["message"] = f"Erreur: {e}"
    finally:
        if client:
            client.close()


@app.post("/api/scan")
def start_scan():
    with _lock:
        if _job["state"] == "running":
            raise HTTPException(409, "Un job est déjà en cours")
        _job.update(
            {
                "kind": "scan",
                "state": "running",
                "message": "Démarrage…",
                "error": None,
                "done": 0,
                "total": 0,
                "result": None,
            }
        )
    threading.Thread(target=_run_scan, name="datefix-scan", daemon=True).start()
    return {"ok": True}


def _run_apply(pattern_ids: list[str], dry_run: bool) -> None:
    client = None
    try:
        if not _last_scan:
            raise RuntimeError("Lance un scan d’abord")
        client = _client()
        selected_n = sum(
            1
            for c in _last_scan["candidates"]
            if c.get("pattern_id") in pattern_ids and c.get("id")
        )
        with _lock:
            _job["total"] = selected_n
            _job["done"] = 0
            _job["message"] = (
                f"{'Dry-run' if dry_run else 'Correction'}… 0/{selected_n}"
            )

        def prog(done: int, total: int) -> None:
            with _lock:
                _job["done"] = done
                _job["total"] = total
                label = "Dry-run" if dry_run else "Correction"
                _job["message"] = f"{label}… {done}/{total}"

        res = apply_fixes(
            client,
            _last_scan["candidates"],
            set(pattern_ids),
            dry_run=dry_run,
            progress=prog,
        )
        with _lock:
            _job["state"] = "done"
            _job["done"] = res["selected"]
            _job["total"] = res["selected"]
            _job["result"] = res
            _job["error"] = None
            if dry_run:
                _job["message"] = f"Dry-run OK — {res['selected']} fichier(s)"
            else:
                err_n = len(res.get("errors") or [])
                _job["message"] = (
                    f"Corrigé {res['updated']}/{res['selected']}"
                    + (f" · {err_n} erreur(s)" if err_n else "")
                )
    except Exception as e:
        with _lock:
            _job["state"] = "error"
            _job["error"] = str(e)
            _job["message"] = f"Erreur: {e}"
    finally:
        if client:
            client.close()


@app.post("/api/apply")
def apply(body: ApplyBody):
    if not _last_scan:
        raise HTTPException(400, "Lance un scan d’abord")
    if not body.pattern_ids:
        raise HTTPException(400, "Aucun pattern sélectionné")
    with _lock:
        if _job["state"] == "running":
            raise HTTPException(409, "Un job est déjà en cours")
        _job.update(
            {
                "kind": "apply",
                "state": "running",
                "message": "Démarrage…",
                "error": None,
                "done": 0,
                "total": 0,
                "result": None,
            }
        )
    threading.Thread(
        target=_run_apply,
        args=(list(body.pattern_ids), body.dry_run),
        name="datefix-apply",
        daemon=True,
    ).start()
    return {"ok": True, "started": True, "dry_run": body.dry_run}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
