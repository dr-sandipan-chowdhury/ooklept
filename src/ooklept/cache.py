# ooklept/cache.py

from diskcache import Cache


class PermanentCache(Cache):
    """
    A diskcache.Cache subclass that structurally cannot expire or evict data.

    Every write-path method that could introduce a TTL is overridden to
    reject a non-None `expire` outright, and the constructor forces
    eviction_policy='none' regardless of what's passed in. This is meant
    for data that must never silently disappear (App/Page/User stores),
    as opposed to SessionCache-style stores where TTL is the point.

    NOTE: diskcache's module-level decorators — diskcache.throttle,
    diskcache.barrier, diskcache.memoize_stampede — take a Cache instance
    as an argument and manage their own TTL'd keys directly against it.
    Being standalone functions (not methods on Cache), they CANNOT be
    blocked by subclassing. If you use them against a PermanentCache,
    they will still write TTL'd keys into it. Don't use them against
    this class; use SessionCache (or a plain Cache) for that instead.
    """

    def __init__(self, directory=None, timeout=60, disk=None, **settings):
        # Force eviction_policy regardless of what the caller passed.
        settings["eviction_policy"] = "none"
        kwargs = {}
        if disk is not None:
            kwargs["disk"] = disk
        super().__init__(directory=directory, timeout=timeout, **kwargs, **settings)

    def set(self, key, value, expire=None, read=False, tag=None, retry=False):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r}). "
                "This store is permanent by design — use SessionCache for TTL'd data."
            )
        return super().set(key, value, expire=None, read=read, tag=tag, retry=retry)

    def add(self, key, value, expire=None, read=False, tag=None, retry=False):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r})."
            )
        return super().add(key, value, expire=None, read=read, tag=tag, retry=retry)

    def touch(self, key, expire=None, retry=False):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r}). "
                "touch() with expire=None is a no-op here since keys never expire."
            )
        return super().touch(key, expire=None, retry=retry)

    def push(
        self,
        value,
        prefix=None,
        side="back",
        expire=None,
        read=False,
        tag=None,
        retry=False,
    ):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r})."
            )
        return super().push(
            value,
            prefix=prefix,
            side=side,
            expire=None,
            read=read,
            tag=tag,
            retry=retry,
        )

    def memoize(self, name=None, typed=False, expire=None, tag=None, ignore=()):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r})."
            )
        return super().memoize(
            name=name, typed=typed, expire=None, tag=tag, ignore=ignore
        )


import uuid as uuid_lib
from contextvars import ContextVar, Token

from diskcache import Cache


class SessionCache(Cache):
    """
    Bounded, self-expiring, per-browser-scoped cache for session data.

    Combines what used to be two things — a diskcache.Cache subclass with
    enforced size/expiry/eviction, and a separate ContextVar-based wrapper
    scoping keys to "the current browser" — into one class. All get/set/
    pop/etc. calls are automatically scoped to whichever browser UUID is
    active via set_context(); callers never see or manage the underlying
    key layout.

    Usage (inside a request, after set_context has been called):
        cache.set("user_id", 42)              # scoped to the current browser
        cache.get("user_id")                  # only ever sees ITS OWN data
        cache.rotate()                        # new session id, same data

    Safety invariants (unchanged from before):
      - size, expiry, policy are all required, finite, and validated.
      - 'none' eviction policy is rejected — this store must never grow
        unbounded, since it's driven by untrusted request traffic.
      - No way to create a non-expiring key.
    """

    MAX_SIZE_LIMIT = 10 * 1024 * 1024 * 1024
    VALID_POLICIES = {
        "least-recently-stored",
        "least-recently-used",
        "least-frequently-used",
    }

    DEFAULT_SIZE = 512 * 1024 * 1024
    DEFAULT_EXPIRY = 3600
    DEFAULT_POLICY = "least-recently-used"

    def __init__(
        self,
        directory=None,
        size: int = DEFAULT_SIZE,
        expiry: float = DEFAULT_EXPIRY,
        policy: str = DEFAULT_POLICY,
        timeout: float = 60,
        disk=None,
        **settings,
    ):
        if size is None or size <= 0:
            raise ValueError(
                "SessionCache requires a finite, positive `size` in bytes."
            )
        if size > self.MAX_SIZE_LIMIT:
            raise ValueError(
                f"size={size} exceeds SessionCache.MAX_SIZE_LIMIT ({self.MAX_SIZE_LIMIT})."
            )
        if expiry is None or expiry <= 0:
            raise ValueError(
                "SessionCache requires a finite, positive `expiry` (seconds)."
            )
        if policy not in self.VALID_POLICIES:
            raise ValueError(
                f"policy={policy!r} is not allowed. Must be one of {sorted(self.VALID_POLICIES)}."
            )

        self._default_expiry = expiry

        settings["size_limit"] = size
        settings["eviction_policy"] = policy

        kwargs = {}
        if disk is not None:
            kwargs["disk"] = disk

        super().__init__(directory=directory, timeout=timeout, **kwargs, **settings)

        # context-scoping state — lives on the instance, not module-level,
        # so multiple SessionCache instances never share context by accident
        self._context: ContextVar[str | None] = ContextVar("session_uuid", default=None)
        self._rotated_to: ContextVar[str | None] = ContextVar(
            "rotated_session_id", default=None
        )

    # ---- context management ----

    def set_context(self, browser_uuid: str) -> Token:
        return self._context.set(browser_uuid)

    def reset_context(self, token: Token) -> None:
        self._context.reset(token)

    def _current_uuid(self) -> str:
        uuid_ = self._context.get()
        if uuid_ is None:
            raise RuntimeError(
                "No browser context set — call set_context() before using SessionCache."
            )
        return uuid_

    def _scoped(self, key) -> str:
        return f"{self._current_uuid()}:{key}"

    def _resolve_expiry(self, expire):
        if expire is None:
            return self._default_expiry
        if expire is False:
            raise ValueError(
                "SessionCache does not support non-expiring keys (expire=False)."
            )
        if expire <= 0:
            raise ValueError(f"expire must be positive, got {expire!r}.")
        return expire

    # ---- scoped overrides of Cache's core methods ----

    def set(self, key, value, expire=None, read=False, tag=None, retry=False):
        return super().set(
            self._scoped(key),
            value,
            expire=self._resolve_expiry(expire),
            read=read,
            tag=tag,
            retry=retry,
        )

    def get(
        self, key, default=None, read=False, expire_time=False, tag=False, retry=False
    ):
        return super().get(
            self._scoped(key),
            default=default,
            read=read,
            expire_time=expire_time,
            tag=tag,
            retry=retry,
        )

    def add(self, key, value, expire=None, read=False, tag=None, retry=False):
        return super().add(
            self._scoped(key),
            value,
            expire=self._resolve_expiry(expire),
            read=read,
            tag=tag,
            retry=retry,
        )

    def touch(self, key, expire=None, retry=False):
        return super().touch(
            self._scoped(key), expire=self._resolve_expiry(expire), retry=retry
        )

    def delete(self, key, retry=False):
        return super().delete(self._scoped(key), retry=retry)

    def pop(self, key, default=None, expire_time=False, tag=False, retry=False):
        return super().pop(
            self._scoped(key),
            default=default,
            expire_time=expire_time,
            tag=tag,
            retry=retry,
        )

    def has_key(self, key) -> bool:
        return key in self

    def __contains__(self, key):
        return super().__contains__(self._scoped(key))

    def __getitem__(self, key):
        return super().__getitem__(self._scoped(key))

    def __setitem__(self, key, value):
        return self.set(key, value)  # routes through set() -> enforced expiry

    def __delitem__(self, key):
        return super().__delitem__(self._scoped(key))

    # ---- rotate: move all of the CURRENT session's keys to a new id ----

    def rotate(self) -> str:
        old_uuid = self._current_uuid()
        new_uuid = str(uuid_lib.uuid4())
        prefix = f"{old_uuid}:"

        with self.transact():
            for full_key in list(super().iterkeys()):
                if isinstance(full_key, str) and full_key.startswith(prefix):
                    value, expire_time, tag = super().get(
                        full_key, expire_time=True, tag=True
                    )
                    if expire_time is None:
                        expire_time = (
                            self._default_expiry
                        )  # never let a rotated key become permanent
                    suffix = full_key[len(prefix) :]
                    super().set(
                        f"{new_uuid}:{suffix}", value, expire=expire_time, tag=tag
                    )
                    super().delete(full_key)

        self._context.set(new_uuid)
        self._rotated_to.set(new_uuid)
        return new_uuid

    def get_rotated_id(self) -> str | None:
        return self._rotated_to.get()

    def __iter__(self):
        prefix = f"{self._current_uuid()}:"
        for full_key in super().__iter__():
            if isinstance(full_key, str) and full_key.startswith(prefix):
                yield full_key[len(prefix) :]

    def __len__(self):
        prefix = f"{self._current_uuid()}:"
        return sum(
            1 for k in super().__iter__() if isinstance(k, str) and k.startswith(prefix)
        )
