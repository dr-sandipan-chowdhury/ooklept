# ooklept/stores.py

import os
import re
from collections.abc import Callable
from contextvars import ContextVar, Token
from pathlib import Path

from ooklept.cache import PermanentCache, SessionCache
from ooklept.sharding import shard_index

PRIVATE_DIR_NAME = "private"
DATABASE_DIR_NAME = "ookleptdb"

APP_STORAGE_DIR_NAME = "app"
PAGE_STORAGE_DIR_NAME = "page"
USER_STORAGE_DIR_NAME = "user"
SESSION_STORAGE_DIR_NAME = "session"


PAGE_SHARD_NUM = 8


def set_up_storage_files():
    # cwd will be the folder there serve.py acts
    cwd = os.getcwd()

    database_dir = Path(cwd) / PRIVATE_DIR_NAME / DATABASE_DIR_NAME
    database_dir.mkdir(parents=True, exist_ok=True)

    app_storage_dir = database_dir / APP_STORAGE_DIR_NAME
    app_storage_dir.mkdir(exist_ok=True)

    page_storage_dir = database_dir / PAGE_STORAGE_DIR_NAME
    page_storage_dir.mkdir(exist_ok=True)

    # shardding
    # Check if previously shardded, and if is, then check the number if different raise Error
    # as old data exists that dont match current shardding
    prev_shards = [
        i for i in os.listdir(page_storage_dir) if re.match(r"^shard_[\d]+$", i)
    ]
    if prev_shards and len(prev_shards) != PAGE_SHARD_NUM:
        raise RuntimeError(
            f"Previous sharded data in {page_storage_dir} does not match the current number: {PAGE_SHARD_NUM}, Manually clear the directory."
        )

    for i in range(PAGE_SHARD_NUM):
        (page_storage_dir / f"shard_{i}").mkdir(exist_ok=True)

    user_storage_dir = database_dir / USER_STORAGE_DIR_NAME
    user_storage_dir.mkdir(exist_ok=True)

    session_storage_dir = database_dir / SESSION_STORAGE_DIR_NAME
    session_storage_dir.mkdir(exist_ok=True)


def _get_app_store():
    p = Path(PRIVATE_DIR_NAME) / DATABASE_DIR_NAME / APP_STORAGE_DIR_NAME
    if p.exists() and p.is_dir():
        return PermanentCache(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


def _get_user_store():
    p = Path(PRIVATE_DIR_NAME) / DATABASE_DIR_NAME / USER_STORAGE_DIR_NAME
    if p.exists() and p.is_dir():
        return PermanentCache(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


def _get_page_store(page_path: str):
    shard = shard_index(page_path, PAGE_SHARD_NUM)
    p = (
        Path(PRIVATE_DIR_NAME)
        / DATABASE_DIR_NAME
        / PAGE_STORAGE_DIR_NAME
        / f"shard_{shard}"
    )
    if p.exists() and p.is_dir():
        return PermanentCache(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


def _get_session_store():
    p = Path(PRIVATE_DIR_NAME) / DATABASE_DIR_NAME / SESSION_STORAGE_DIR_NAME
    if p.exists() and p.is_dir():
        return SessionCache(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


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


class Stores:
    def __init__(self):
        self._app_store = None
        self._user_store = None
        self._session_store = None
        self.get_store = ContextStore("get")
        self.post_store = ContextStore("post")
        self._page_stores: dict[int, PermanentCache] = {}

    @property
    def app_store(self):
        if self._app_store is None:
            self._app_store = _get_app_store()
        return self._app_store

    @property
    def user_store(self):
        if self._user_store is None:
            self._user_store = _get_user_store()
        return self._user_store

    @property
    def session_store(self):
        if self._session_store is None:
            self._session_store = _get_session_store()
        return self._session_store

    def page_store(self, page_path: str):
        shard = shard_index(page_path, PAGE_SHARD_NUM)
        if shard not in self._page_stores:
            self._page_stores[shard] = _get_page_store(page_path)
        return self._page_stores[shard]


stores = Stores()  # now safe — no filesystem access happens here
