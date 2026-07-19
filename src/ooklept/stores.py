# ooklept/stores.py

from collections.abc import MutableMapping
from contextvars import ContextVar, Token


class Stores:
    def __init__(self):
        self.Global = {}
        self.Local = LocalStore()
        self.Get = ContextStore("get")
        self.Post = ContextStore("post")

class LocalStore(MutableMapping):
    def __init__(self):
        self._data = {}
        self._local_context: ContextVar[str | None] = ContextVar(
            "current_browser_context", default=None
        )

    def _set_context(self, browser_uuid: str):
        token = self._local_context.set(browser_uuid)
        self._data.setdefault(browser_uuid, {})
        return token

    def _reset_context(self, token: Token):
        self._local_context.reset(token)

    def _current_dict(self) -> dict:
        uuid = self._local_context.get()
        if uuid is None:
            raise RuntimeError("No browser context")
        return self._data.setdefault(uuid, {})


    def __getitem__(self, key):
        return self._current_dict()[key]

    def __setitem__(self, key, value):
        self._current_dict()[key] = value

    def __delitem__(self, key):
        del self._current_dict()[key]

    def __iter__(self):
        return iter(self._current_dict())

    def __len__(self):
        return len(self._current_dict())

    def __repr__(self):
        return repr(self._current_dict())

    def __str__(self):
        return str(self._current_dict())


class ContextStore(MutableMapping):
    def __init__(self, name: str):
        self._context: ContextVar[dict] = ContextVar(name, default={})

    def _set_context(self, value: dict):
        return self._context.set(value)

    def _reset_context(self, token: Token):
        self._context.reset(token)

    def _current_dict(self) -> dict:
        return self._context.get()

    def __getitem__(self, key):
        return self._current_dict()[key]

    def __setitem__(self, key, value):
        self._current_dict()[key] = value

    def __delitem__(self, key):
        del self._current_dict()[key]

    def __iter__(self):
        return iter(self._current_dict())

    def __len__(self):
        return len(self._current_dict())

    def __repr__(self):
        return repr(self._current_dict())

    def __str__(self):
        return str(self._current_dict())

stores = Stores()
