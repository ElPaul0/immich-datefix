from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.auth import AuthStore
from app.config import get_settings
from app.immich import ImmichClient, ImmichError
from app.scanner import apply_fixes, patterns_catalog, scan_library

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
settings = get_settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = settings.data_dir / "config.json"
COOKIE_NAME = "datefix_session"

app = FastAPI(title="immich-datefix", version="0.3.0")
auth = AuthStore(settings.data_dir)

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


def _legacy_defaults() -> tuple[str, str]:
    """Fallback URL / key from env or old global config.json."""
    cfg = _load_cfg()
    url = (cfg.get("immich_url") or settings.immich_url).rstrip("/")
    key = cfg.get("immich_api_key") or settings.immich_api_key
    return url, key


def _session_user(request: Request) -> dict[str, Any] | None:
    token = request.cookies.get(COOKIE_NAME)
    sess = auth.get_session(token)
    if not sess:
        return None
    return auth.get_user(sess["username"])


def require_user(request: Request) -> dict[str, Any]:
    user = _session_user(request)
    if not user:
        raise HTTPException(401, "Non connecté")
    return user


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=30 * 86400,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


def _resolved_for(user: dict[str, Any]) -> tuple[str, str]:
    legacy_url, _ = _legacy_defaults()
    url = (user.get("immich_url") or legacy_url or settings.immich_url).rstrip("/")
    key = user.get("immich_api_key") or ""
    return url, key


def _client_for(user: dict[str, Any]) -> ImmichClient:
    url, key = _resolved_for(user)
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
            "scanned": done if _job["kind"] == "scan" else _last_scan["scanned"] if _last_scan else 0,
        }


class RegisterBody(BaseModel):
    username: str
    pin: str
    immich_api_key: str
    immich_url: str | None = None


class LoginBody(BaseModel):
    username: str
    pin: str


class SettingsBody(BaseModel):
    immich_url: str | None = None
    immich_api_key: str | None = None
    pin: str | None = None


class ApplyBody(BaseModel):
    pattern_ids: list[str] = Field(default_factory=list)
    dry_run: bool = True


@app.get("/api/health")
def health():
    return {"ok": True, "version": "0.3.0"}


@app.get("/api/auth/status")
def auth_status(request: Request):
    needs_setup = auth.user_count() == 0
    user = _session_user(request)
    legacy_url, legacy_key = _legacy_defaults()
    out: dict[str, Any] = {
        "authenticated": user is not None,
        "needs_setup": needs_setup,
        "default_immich_url": legacy_url,
        "has_legacy_key": bool(legacy_key) and needs_setup,
    }
    if user:
        out["user"] = auth.public_user(user)
    return out


@app.post("/api/auth/register")
def auth_register(body: RegisterBody, response: Response, request: Request):
    # First user: open setup. Later: only while logged in.
    first = auth.user_count() == 0
    if not first:
        require_user(request)

    legacy_url, _ = _legacy_defaults()
    try:
        user = auth.create_user(
            body.username,
            body.pin,
            body.immich_api_key,
            immich_url=body.immich_url or legacy_url,
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    # Auto-login only on first account (setup); keep current session when adding users.
    if first:
        token = auth.create_session(user["username"])
        _set_session_cookie(response, token)
    return {"ok": True, "user": auth.public_user(user), "logged_in": first}


@app.post("/api/auth/login")
def auth_login(body: LoginBody, response: Response):
    user = auth.authenticate(body.username, body.pin)
    if not user:
        raise HTTPException(401, "Identifiant ou PIN incorrect")
    token = auth.create_session(user["username"])
    _set_session_cookie(response, token)
    return {"ok": True, "user": auth.public_user(user)}


@app.post("/api/auth/logout")
def auth_logout(request: Request, response: Response):
    auth.delete_session(request.cookies.get(COOKIE_NAME))
    _clear_session_cookie(response)
    return {"ok": True}


@app.get("/api/patterns")
def api_patterns(_user: dict = Depends(require_user)):
    return {"patterns": patterns_catalog()}


@app.get("/api/settings")
def get_settings_api(user: dict = Depends(require_user)):
    url, key = _resolved_for(user)
    return {
        "username": user["username"],
        "immich_url": url,
        "has_api_key": bool(key),
        "api_key_hint": (key[:4] + "…" + key[-4:]) if key and len(key) > 10 else "",
        "min_delta_seconds": settings.min_delta_seconds,
        "default_hour": settings.default_hour,
    }


@app.post("/api/settings")
def set_settings_api(body: SettingsBody, user: dict = Depends(require_user)):
    try:
        auth.update_user(
            user["username"],
            immich_url=body.immich_url,
            immich_api_key=body.immich_api_key,
            pin=body.pin,
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    refreshed = auth.get_user(user["username"]) or user
    url, key = _resolved_for(refreshed)
    return {
        "username": refreshed["username"],
        "immich_url": url,
        "has_api_key": bool(key),
        "api_key_hint": (key[:4] + "…" + key[-4:]) if key and len(key) > 10 else "",
        "min_delta_seconds": settings.min_delta_seconds,
        "default_hour": settings.default_hour,
    }


@app.post("/api/ping")
def ping(user: dict = Depends(require_user)):
    try:
        client = _client_for(user)
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
def job_status(_user: dict = Depends(require_user)):
    return _job_snapshot()


def _run_scan(username: str) -> None:
    global _last_scan
    client = None
    try:
        user = auth.get_user(username)
        if not user:
            raise RuntimeError("Session invalide")
        client = _client_for(user)
        with _lock:
            _job["message"] = "Scan Immich…"
            _job["done"] = 0
            _job["total"] = 0

        def prog(n: int) -> None:
            with _lock:
                _job["done"] = n
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
def start_scan(user: dict = Depends(require_user)):
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
    threading.Thread(
        target=_run_scan,
        args=(user["username"],),
        name="datefix-scan",
        daemon=True,
    ).start()
    return {"ok": True}


def _run_apply(username: str, pattern_ids: list[str], dry_run: bool) -> None:
    client = None
    try:
        if not _last_scan:
            raise RuntimeError("Lance un scan d’abord")
        user = auth.get_user(username)
        if not user:
            raise RuntimeError("Session invalide")
        client = _client_for(user)
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
def apply(body: ApplyBody, user: dict = Depends(require_user)):
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
        args=(user["username"], list(body.pattern_ids), body.dry_run),
        name="datefix-apply",
        daemon=True,
    ).start()
    return {"ok": True, "started": True, "dry_run": body.dry_run}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
