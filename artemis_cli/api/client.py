"""Core HTTP client — handles auth, cookie storage, and error mapping."""
import httpx
from typing import Any

from artemis_cli import config


class ArtemisError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(message)


class ArtemisClient:
    def __init__(self, server: str | None = None, token: str | None = None):
        self.server = (server or config.get_server() or "").rstrip("/")
        if not self.server:
            raise ArtemisError(0, "Not logged in. Run: artemis login")
        self._token = token or config.get_token()
        if not self._token:
            raise ArtemisError(401, "No auth token found. Run: artemis login")

    def _headers(self) -> dict:
        return {"Cookie": f"jwt={self._token}", "Content-Type": "application/json"}

    def _url(self, path: str) -> str:
        return f"{self.server}/api/{path.lstrip('/')}"

    def _raise_for_status(self, r: httpx.Response) -> None:
        if r.is_success:
            return
        try:
            detail = r.json().get("message") or r.json().get("title") or r.text
        except Exception:
            detail = r.text or r.reason_phrase
        raise ArtemisError(r.status_code, f"HTTP {r.status_code}: {detail}")

    def get(self, path: str, **kwargs) -> Any:
        with httpx.Client(follow_redirects=True) as client:
            r = client.get(self._url(path), headers=self._headers(), **kwargs)
        self._raise_for_status(r)
        return r.json() if r.content else None

    def post(self, path: str, json: Any = None, **kwargs) -> Any:
        with httpx.Client(follow_redirects=True) as client:
            r = client.post(self._url(path), headers=self._headers(), json=json, **kwargs)
        self._raise_for_status(r)
        return r.json() if r.content else None

    def put(self, path: str, json: Any = None, **kwargs) -> Any:
        with httpx.Client(follow_redirects=True) as client:
            r = client.put(self._url(path), headers=self._headers(), json=json, **kwargs)
        self._raise_for_status(r)
        return r.json() if r.content else None

    def patch(self, path: str, json: Any = None, **kwargs) -> Any:
        with httpx.Client(follow_redirects=True) as client:
            r = client.patch(self._url(path), headers=self._headers(), json=json, **kwargs)
        self._raise_for_status(r)
        return r.json() if r.content else None

    def delete(self, path: str, **kwargs) -> None:
        with httpx.Client(follow_redirects=True) as client:
            r = client.delete(self._url(path), headers=self._headers(), **kwargs)
        self._raise_for_status(r)

    def get_bytes(self, path: str, **kwargs) -> bytes:
        with httpx.Client(follow_redirects=True) as client:
            r = client.get(self._url(path), headers=self._headers(), **kwargs)
        self._raise_for_status(r)
        return r.content


def login(server: str, username: str, password: str, remember_me: bool = True) -> str:
    """Authenticate and return the JWT token."""
    url = f"{server.rstrip('/')}/api/core/public/authenticate"
    with httpx.Client(follow_redirects=True) as client:
        r = client.post(url, json={"username": username, "password": password, "rememberMe": remember_me})
    if not r.is_success:
        try:
            detail = r.json().get("message") or r.text
        except Exception:
            detail = r.text
        raise ArtemisError(r.status_code, f"Login failed: {detail}")

    # JWT arrives either in response body or as a Set-Cookie header
    token = None
    try:
        token = r.json().get("access_token") or r.json().get("id_token")
    except Exception:
        pass

    if not token:
        # Fall back to cookie
        token = r.cookies.get("jwt")

    if not token:
        raise ArtemisError(0, "Login succeeded but no token received — unexpected response format")

    return token


def get_client() -> ArtemisClient:
    """Return a ready-to-use client, raising a friendly error if not logged in."""
    return ArtemisClient()
