"""Persistent config stored in ~/.artemis/config.json"""
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".artemis"
CONFIG_FILE = CONFIG_DIR / "config.json"
KEYRING_SERVICE = "artemis-cli"


def _load() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def _save(data: dict) -> None:
    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    try:
        CONFIG_FILE.chmod(0o600)
    except OSError:
        pass  # chmod is a no-op on Windows


def get(key: str, default=None):
    return _load().get(key, default)


def put(key: str, value) -> None:
    data = _load()
    data[key] = value
    _save(data)


def delete(key: str) -> None:
    data = _load()
    data.pop(key, None)
    _save(data)


def get_server() -> str | None:
    return get("server")


def get_token() -> str | None:
    """Return stored JWT token (keyring first, config.json as fallback)."""
    try:
        import keyring
        token = keyring.get_password(KEYRING_SERVICE, get_server() or "")
        if token:
            return token
    except Exception:
        pass
    return get("token")


def save_session(server: str, token: str) -> None:
    server = server.rstrip("/")
    data = _load()
    data["server"] = server
    try:
        import keyring
        keyring.set_password(KEYRING_SERVICE, server, token)
        data.pop("token", None)
    except Exception:
        data["token"] = token
    _save(data)


def clear_session() -> None:
    server = get_server()
    try:
        import keyring
        if server:
            keyring.delete_password(KEYRING_SERVICE, server)
    except Exception:
        pass
    data = _load()
    data.pop("token", None)
    data.pop("server", None)
    _save(data)
