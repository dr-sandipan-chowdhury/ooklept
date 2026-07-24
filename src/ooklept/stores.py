# ooklept/stores.py

import os
import re
from pathlib import Path

from ooklept.sharding import shard_index
from ooklept.storage_classes import ContextStore, PermanentStore, SessionStore

PRIVATE_DIR_NAME = "private"
DATABASE_DIR_NAME = "ookleptdb"

APP_STORAGE_DIR_NAME = "app"
PAGE_STORAGE_DIR_NAME = "page"
USER_STORAGE_DIR_NAME = "user"
SESSION_STORAGE_DIR_NAME = "session"


PAGE_SHARD_NUM = 8


# Internal Functions
def _set_up_storage_files():
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
        return PermanentStore(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


def _get_user_store():
    p = Path(PRIVATE_DIR_NAME) / DATABASE_DIR_NAME / USER_STORAGE_DIR_NAME
    if p.exists() and p.is_dir():
        return PermanentStore(p)
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
        return SessionStore(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


class Stores:
    """
    Gives access to 6 different types storage of the App.
    # App Storage:
        - It is an app level global storage that can be accessed by any [page].py
        - Accessed via `stores.app_store`
    # Page Storage:
        - It is an page level global storage that can be accessed only by a specific [page].py
        - Accessed via `stores.page_store(path)`
    # User Storage:
        - It is an user specific storage for the currently logged in user
        - Accessed via `stores.user_store`
    # Session Storage:
        - It is a browser specific storage bound to a specific session in that browser.
        - Accessed via `stores.session_store`
    # Get Storage:
        - It is a per-request storage containing query data from a get request
        - Accessed via `stores.get_store`
    # Post Storage:
        - It is a per-request storage containing form data from a post request
        - Accessed via `stores.post_store`
    """

    def __init__(self):
        self._app_store = None
        self._user_store = None
        self._session_store = None
        self.get_store = ContextStore("get")
        self.post_store = ContextStore("post")
        self._page_stores: dict[int, PermanentStore] = {}

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


stores = Stores()
