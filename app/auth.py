"""PIN users + server-side sessions (API key stored per user)."""

from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
from pathlib import Path
from typing import Any


_PBKDF2_ITERS = 200_000
_SESSION_DAYS = 30


class AuthStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.users_path = data_dir / "users.json"
        self.sessions_path = data_dir / "sessions.json"
        self._lock = threading.Lock()
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def _write_json(self, path: Path, data: Any) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)

    @staticmethod
    def hash_pin(pin: str, salt: str | None = None) -> tuple[str, str]:
        salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            pin.encode("utf-8"),
            salt.encode("utf-8"),
            _PBKDF2_ITERS,
        ).hex()
        return salt, digest

    @staticmethod
    def verify_pin(pin: str, salt: str, digest: str) -> bool:
        _, got = AuthStore.hash_pin(pin, salt)
        return secrets.compare_digest(got, digest)

    @staticmethod
    def normalize_username(username: str) -> str:
        return username.strip().lower()

    @staticmethod
    def validate_pin(pin: str) -> str | None:
        pin = (pin or "").strip()
        if not pin.isdigit() or not (4 <= len(pin) <= 8):
            return "PIN invalide (4 à 8 chiffres)"
        return None

    def list_users(self) -> list[dict[str, Any]]:
        with self._lock:
            raw = self._read_json(self.users_path, {"users": []})
            return list(raw.get("users") or [])

    def user_count(self) -> int:
        return len(self.list_users())

    def get_user(self, username: str) -> dict[str, Any] | None:
        key = self.normalize_username(username)
        for u in self.list_users():
            if u.get("username") == key:
                return u
        return None

    def create_user(
        self,
        username: str,
        pin: str,
        immich_api_key: str,
        immich_url: str | None = None,
    ) -> dict[str, Any]:
        err = self.validate_pin(pin)
        if err:
            raise ValueError(err)
        name = self.normalize_username(username)
        if not name or len(name) < 2:
            raise ValueError("Nom d’utilisateur trop court")
        if not immich_api_key.strip():
            raise ValueError("Clé API Immich requise")
        with self._lock:
            raw = self._read_json(self.users_path, {"users": []})
            users = list(raw.get("users") or [])
            if any(u.get("username") == name for u in users):
                raise ValueError("Cet utilisateur existe déjà")
            salt, digest = self.hash_pin(pin.strip())
            user = {
                "username": name,
                "pin_salt": salt,
                "pin_hash": digest,
                "immich_api_key": immich_api_key.strip(),
                "immich_url": (immich_url or "").strip().rstrip("/") or None,
                "created_at": int(time.time()),
            }
            users.append(user)
            self._write_json(self.users_path, {"users": users})
            return user

    def update_user(
        self,
        username: str,
        *,
        immich_api_key: str | None = None,
        immich_url: str | None = None,
        pin: str | None = None,
    ) -> dict[str, Any]:
        key = self.normalize_username(username)
        with self._lock:
            raw = self._read_json(self.users_path, {"users": []})
            users = list(raw.get("users") or [])
            found = None
            for u in users:
                if u.get("username") == key:
                    found = u
                    break
            if not found:
                raise ValueError("Utilisateur introuvable")
            if pin is not None and pin.strip():
                err = self.validate_pin(pin)
                if err:
                    raise ValueError(err)
                salt, digest = self.hash_pin(pin.strip())
                found["pin_salt"] = salt
                found["pin_hash"] = digest
            if immich_api_key is not None and immich_api_key.strip():
                found["immich_api_key"] = immich_api_key.strip()
            if immich_url is not None:
                found["immich_url"] = immich_url.strip().rstrip("/") or None
            self._write_json(self.users_path, {"users": users})
            return found

    def authenticate(self, username: str, pin: str) -> dict[str, Any] | None:
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_pin(pin.strip(), user["pin_salt"], user["pin_hash"]):
            return None
        return user

    def _load_sessions(self) -> dict[str, Any]:
        return self._read_json(self.sessions_path, {"sessions": {}})

    def create_session(self, username: str) -> str:
        token = secrets.token_urlsafe(32)
        expires = int(time.time()) + _SESSION_DAYS * 86400
        with self._lock:
            data = self._load_sessions()
            sessions = dict(data.get("sessions") or {})
            # drop expired
            now = int(time.time())
            sessions = {
                k: v
                for k, v in sessions.items()
                if int(v.get("expires", 0)) > now
            }
            sessions[token] = {
                "username": self.normalize_username(username),
                "expires": expires,
                "created_at": now,
            }
            self._write_json(self.sessions_path, {"sessions": sessions})
        return token

    def get_session(self, token: str | None) -> dict[str, Any] | None:
        if not token:
            return None
        with self._lock:
            data = self._load_sessions()
            sessions = dict(data.get("sessions") or {})
            sess = sessions.get(token)
            if not sess:
                return None
            if int(sess.get("expires", 0)) <= int(time.time()):
                sessions.pop(token, None)
                self._write_json(self.sessions_path, {"sessions": sessions})
                return None
            return sess

    def delete_session(self, token: str | None) -> None:
        if not token:
            return
        with self._lock:
            data = self._load_sessions()
            sessions = dict(data.get("sessions") or {})
            if token in sessions:
                sessions.pop(token, None)
                self._write_json(self.sessions_path, {"sessions": sessions})

    def public_user(self, user: dict[str, Any]) -> dict[str, Any]:
        key = user.get("immich_api_key") or ""
        return {
            "username": user["username"],
            "immich_url": user.get("immich_url"),
            "has_api_key": bool(key),
            "api_key_hint": (key[:4] + "…" + key[-4:]) if key and len(key) > 10 else "",
        }
