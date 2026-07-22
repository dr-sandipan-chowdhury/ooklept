# ooklept/stores.py

import time
from contextvars import ContextVar, Token
from threading import RLock
from typing import Any, Callable


def post_track(name, default, converter:Callable = str):
    if stores.post_store.has_key(name):
        pn = stores.post_store.get(name)
        return converter(pn)
    else:
        return default

def get_track(name, default, converter = str):
    if stores.get_store.has_key(name):
        gn = stores.get_store.get(name)
        return converter(gn)
    else:
        return default




class Stores:
    def __init__(self):
        self.global_store = GlobalStore()
        self.session_store = SessionStore()
        self.get_store = ContextStore("get")
        self.post_store = ContextStore("post")


class GlobalStore:
    def __init__(self):
        self._data = {}
        self._lock = RLock()

    def set(self, key, value):
        with self._lock:
            self._data[key] = value

    def get(self, key):
        with self._lock:
            v = self._data.get(key)
            if hasattr(v, "copy"):
                return v.copy()
            return v

    def setdefault(self, key, value):
        with self._lock:
            v = self._data.setdefault(key, value)
            if hasattr(v, "copy"):
                return v.copy()
            return v

    def pop(self, key, *default):
        with self._lock:
            v = self._data.pop(key, *default)
            if hasattr(v, "copy"):
                return v.copy()
            return v

    def has_key(self, key)->bool:
        with self._lock:
            return key in self._data

    def __len__(self):
        with self._lock:
            return len(self._data)


class SessionStore:
    def __init__(self):
        self._data = {}
        self._lock = RLock()
        self._context: ContextVar[str | None] = ContextVar(
            "current_browser_context", default=None
        )
        self._last_clean_up = 0
        self._clean_up_interval = 600 # scannig happens at this interval
        self._dead_session_threshold = 3600 # after how much time of inactivity the session data will be deleted

    def set_context(self, browser_uuid: str):
        token = self._context.set(browser_uuid)
        with self._lock:
            self._data.setdefault(
                browser_uuid, {"memory": {}, "last_seen": time.monotonic()}
            )
            self._data[browser_uuid]["last_seen"] = time.monotonic()
        return token

    def reset_context(self, token: Token):
        self._context.reset(token)

    def _current_dict(self) -> dict:
        uuid = self._context.get()
        if uuid is None:
            raise RuntimeError("No browser context")
        with self._lock:
            self._data.setdefault(uuid, {"memory": {}, "last_seen": time.monotonic()})
            return self._data[uuid]["memory"]

    def get(self, key: str):
        "returns a copy of value, so your mutation to value does not reflect in original stores.Local"
        with self._lock:
            v = self._current_dict().get(key)
            if hasattr(v, "copy"):
                return v.copy()
            return v

    def set(self, key: str, value: Any):
        with self._lock:
            self._current_dict()[key] = value

    def setdefault(self, key: str, value: Any):
        with self._lock:
            v = self._current_dict().setdefault(key, value)
            if hasattr(v, "copy"):
                return v.copy()
            return v

    def pop(self, key: str, *default):
        with self._lock:
            v = self._current_dict().pop(key, *default)
            if hasattr(v, "copy"):
                return v.copy()
            return v

    def has_key(self, key)->bool:
        with self._lock:
            return key in self._current_dict()

    def __len__(self):
        with self._lock:
            return len(self._current_dict())

    def cleanup_stale_sessions(self):
        now = time.monotonic()
        if time.monotonic() - self._last_clean_up > self._clean_up_interval:
            with self._lock:
                stale = [
                    uuid for uuid, session in self._data.items()
                    if now - session["last_seen"] > self._dead_session_threshold
                ]
                for uuid in stale:
                    del self._data[uuid]
                self._last_clean_up = time.monotonic()


class ContextStore:
    def __init__(self, name: str):
        self.name = name
        self._context: ContextVar[dict|None] = ContextVar(name, default=None)

    def set_context(self, value: dict):
        return self._context.set(value)

    def reset_context(self, token: Token):
        self._context.reset(token)

    def _current_dict(self) -> dict:
        d = self._context.get()
        if d is None:
            raise RuntimeError(f"No context provided for store: {self.name}")
        return d

    def get(self, key):
        return self._current_dict().get(key)

    def set(self, key, value):
        self._current_dict()[key] = value

    def setdefault(self, key, value):
        return self._current_dict().setdefault(key, value)

    def pop(self, key, *default):
        return self._current_dict().pop(key, *default)

    def has_key(self, key)->bool:
        return key in self._current_dict()

    def __len__(self):
        return len(self._current_dict())


stores = Stores()
