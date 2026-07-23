# ooklept/stores.py

import time
from contextvars import ContextVar, Token
from threading import RLock
from typing import Any, Callable, Iterable
from uuid import uuid4


def post_track(name, default, converter: Callable = str):
    if stores.post_store.has_key(name):
        pn = stores.post_store.get(name)
        return converter(pn)
    else:
        return default


def get_track(name, default, converter=str):
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
    def transaction(self):
        """
        Hold the store lock for a block of multiple operations that must
        appear atomic together — e.g. reading two keys and writing both
        based on each other (a transfer between them).

        with stores.global_store.transaction():
            a = stores.global_store.get("account_a")
            b = stores.global_store.get("account_b")
            stores.global_store.set("account_a", a - 100)
            stores.global_store.set("account_b", b + 100)

        Nothing else can touch this store while the block is open,
        including OTHER USERS' unrelated requests — this is shared,
        global state. Keep the block short. Never do slow work (I/O,
        sleeps, network calls) inside it.

        Prefer update() for single-key read-modify-write, or map() for
        the same transform across many keys — reach for transaction()
        only when the logic genuinely doesn't fit either shape.
        """
        return self._lock  # RLock is already a context manager

    def map(self, fn: Callable[[str, Any], Any], keys: Iterable[str] | None = None):
        """
        Atomically apply fn(key, value) -> new_value across multiple keys
        as one batch. Holds the lock for the entire operation, so no other
        thread's read or write can interleave between keys, and the key
        set can't shift under you mid-iteration.

        Pass `keys` to restrict to a known subset — locks the store for
        less time than mapping over everything.

        Do NOT do slow work (I/O, sleeps, network calls) inside fn — it
        blocks every other request's access to this store for as long
        as the batch takes.
        """
        with self._lock:
            target_keys = list(keys) if keys is not None else list(self._data.keys())
            for k in target_keys:
                if k in self._data:
                    self._data[k] = fn(k, self._data[k])

    def update(self, key, fn: Callable[[Any], Any], default=None):
        """
        Atomically read-modify-write a value. `fn` receives the current
        value (or `default` if unset) and must return the new value —
        it should not rely on mutating in place; return a new object.

        This closes the lost-update race that plain get()+set() has,
        since the whole read-transform-write happens under one lock
        acquisition, with no other thread's set() able to interleave.
        """
        with self._lock:
            current = self._data.get(key, default)
            new_value = fn(current)
            self._data[key] = new_value
            return new_value

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

    def has_key(self, key) -> bool:
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
        self._clean_up_interval = 600  # scannig happens at this interval
        self._dead_session_threshold = (
            3600  # after how much time of inactivity the session data will be deleted
        )
        # tracks whether rotate() was called during the current request,
        # so serve.py knows to issue a new cookie
        self._rotated_to: ContextVar[str | None] = ContextVar(
            "rotated_session_id", default=None
        )

    def transaction(self):
        """
        Hold the store lock for a block of multiple operations on THIS
        session that must appear atomic together — e.g. moving an item
        between two keys in the same user's session data.

        with stores.session_store.transaction():
            cart = stores.session_store.get("cart")
            saved = stores.session_store.get("saved_for_later")
            stores.session_store.set("cart", [i for i in cart if i != x])
            stores.session_store.set("saved_for_later", saved + [x])

        Blocks concurrent requests from the SAME browser (multiple tabs,
        parallel fetch() calls) from touching this store until the block
        exits — it does not affect other users' sessions. Keep the block
        short; never do slow work (I/O, sleeps, network calls) inside it.

        Requires a browser context to already be set (true for any code
        running inside a page script during normal request handling).

        Prefer update() for single-key read-modify-write, or map() for
        the same transform across many keys — reach for transaction()
        only when the logic genuinely doesn't fit either shape.
        """
        return self._lock  # RLock is already a context manager

    def update(self, key, fn: Callable[[Any], Any], default=None):
        """
        Atomically read-modify-write a value. `fn` receives the current
        value (or `default` if unset) and must return the new value —
        it should not rely on mutating in place; return a new object.

        This closes the lost-update race that plain get()+set() has,
        since the whole read-transform-write happens under one lock
        acquisition, with no other thread's set() able to interleave.
        """
        with self._lock:
            current = self._current_dict().get(key, default)
            new_value = fn(current)
            self._current_dict()[key] = new_value
            return new_value

    def map(self, fn: Callable[[str, Any], Any], keys: Iterable[str] | None = None):
        """
        Atomically apply fn(key, value) -> new_value across multiple keys
        as one batch. Holds the lock for the entire operation, so no other
        thread's read or write can interleave between keys, and the key
        set can't shift under you mid-iteration.

        Pass `keys` to restrict to a known subset — locks the store for
        less time than mapping over everything.

        Do NOT do slow work (I/O, sleeps, network calls) inside fn — it
        blocks every other request's access to this store for as long
        as the batch takes.
        """
        with self._lock:
            current = self._current_dict()
            target_keys = list(keys) if keys is not None else list(current.keys())
            for k in target_keys:
                if k in current:
                    current[k] = fn(k, current[k])

    def rotate(self) -> str:
        """
        Replace the current session's ID with a freshly generated one,
        carrying over its existing data. Call this right after a
        privilege change (e.g. successful login) to prevent session
        fixation from a pre-authentication session ID.

        Returns the new session id. The caller doesn't need to do
        anything else with it — serve.py picks it up automatically
        and issues the new signed cookie in the response.
        """
        old_uuid = self._context.get()
        if old_uuid is None:
            raise RuntimeError("No browser context")

        new_uuid = str(uuid4())

        with self._lock:
            session = self._data.pop(
                old_uuid, {"memory": {}, "last_seen": time.monotonic()}
            )
            session["last_seen"] = time.monotonic()
            self._data[new_uuid] = session

        # redirect the *current* context to the new id so any further
        # store.get()/set() calls in this same request still work
        self._context.set(new_uuid)
        self._rotated_to.set(new_uuid)

        return new_uuid

    def get_rotated_id(self) -> str | None:
        """Internal: used by serve.py to detect a rotation happened."""
        return self._rotated_to.get()

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

    def has_key(self, key) -> bool:
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
                    uuid
                    for uuid, session in self._data.items()
                    if now - session["last_seen"] > self._dead_session_threshold
                ]
                for uuid in stale:
                    del self._data[uuid]
                self._last_clean_up = time.monotonic()


class ContextStore:
    def __init__(self, name: str):
        self.name = name
        self._context: ContextVar[dict | None] = ContextVar(name, default=None)

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

    def has_key(self, key) -> bool:
        return key in self._current_dict()

    def __len__(self):
        return len(self._current_dict())


stores = Stores()
