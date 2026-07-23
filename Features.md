# Upcoming Features
* Instead of single `GlobalStore` use per-app or per-page Storage
* Move sessions to Redis with TTL to stop unbound session creation
* Pronlem: In-memory-only stores don't scale horizontally. GlobalStore/SessionStore live in process memory, so running multiple worker processes (which you'll want for the blocking-event-loop issue above) breaks session/global-store consistency between workers. This needs an external backing store option before it's production-viable at any real scale.
* New Storage System:
  * App Store: Storage for Whole Application. Per App. i.e. One Always. [Permanent] :SQLITE
  * Page Store: Storage for A Page/Route. Per Page. [Permanent] :SQLITE
  * Session Store: Storage for a Session. Per Browser[Temoprary] :Redis with TTL
  * Get/Post Store: Per request Storage. [Ultrashort]
  * User Store: User's Storage. [Permanent] :SQLITE

# Idea from Claude
This is the one where I'd genuinely slow down and think about interface design first, because the fix isn't "swap in Redis" — it's "make the storage backend swappable at all," since right now `GlobalStore` and `SessionStore` bake "it's a Python dict in this process" into their implementation, not just their behavior.

## The core design move: separate the interface from the backend

Right now, `set()`, `get()`, `update()`, `map()`, `transaction()` are all implemented directly against `self._data` (a dict) and `self._lock` (a threading `RLock`). To support Redis without a rewrite, define a small **backend protocol** that both the in-memory dict and Redis can satisfy, and have `GlobalStore`/`SessionStore` delegate to whichever backend is configured:

```python
from typing import Protocol, Any, Callable, Iterable

class StoreBackend(Protocol):
    def get(self, key: str, default=None) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...
    def pop(self, key: str, *default) -> Any: ...
    def has_key(self, key: str) -> bool: ...
    def update(self, key: str, fn: Callable[[Any], Any], default=None) -> Any: ...
    def map(self, fn: Callable[[str, Any], Any], keys: Iterable[str] | None) -> None: ...
    def transaction(self):  # context manager
        ...
```

`GlobalStore` becomes a thin wrapper choosing a backend at construction:

```python
class GlobalStore:
    def __init__(self, backend: StoreBackend | None = None):
        self._backend = backend or InMemoryBackend()

    def get(self, key, default=None):
        return self._backend.get(key, default)
    # ... delegate everything else the same way
```

This is the single most important structural change — everything below (Redis, TTLs, multi-worker consistency) hangs off this seam. Without it, adding Redis means duplicating and diverging your whole store API a second time.

## Why Redis specifically fits your shape well

- **Solves the multi-worker problem directly.** Each worker process currently has its own `_data` dict — that's the actual bug. Redis is one external process all workers talk to over a socket, so `GlobalStore` becomes genuinely global across workers, not per-worker-and-therefore-inconsistent.
- **Gets you TTL-based session expiry for free**, replacing your manual `cleanup_stale_sessions()` sweep — `SET key value EX 3600` just expires itself; no polling loop, no missed-flood-between-sweeps gap (which also mitigates the memory-exhaustion issue from earlier, as a side benefit).
- **`update()` and `map()` translate cleanly** via Redis transactions (`WATCH`/`MULTI`/`EXEC`, optimistic locking) or, more robustly, **Lua scripts** run via `EVAL` — Redis guarantees a Lua script executes atomically, uninterrupted by other clients, which maps almost exactly onto what your `_lock`-based `update()` does today:

```python
UPDATE_SCRIPT = """
local current = redis.call('GET', KEYS[1])
local new_value = ARGV[1]  -- computed value passed in from Python... 
"""
```
  In practice, `update(key, fn)` is easiest implemented in Python as: fetch, compute `fn(current)`, then use Redis's `WATCH`+`MULTI`+`EXEC` optimistic-lock pattern, retrying on conflict (Redis's own recommended pattern for exactly this read-modify-write case) — cleaner than hand-writing Lua for arbitrary Python callables, since `fn` is arbitrary Python code that can't run inside Redis's Lua sandbox anyway.

- **`transaction()` gets harder, honestly** — this is the part to be upfront about rather than paper over. Redis's `MULTI`/`EXEC` is genuinely different from a Python thread lock: commands queue and execute atomically, but you can't do "get value, branch in Python, then conditionally set" inside a single `MULTI` block the way you can inside a `with lock:` block, because Redis doesn't execute Python inside its transaction — only Redis commands. The `WATCH`-based optimistic pattern handles most of your `transaction()` use cases (read a few keys, compute, write a few keys, retry if something changed underneath you), but it's a genuinely different concurrency model (optimistic + retry, vs. your current pessimistic + block), worth documenting as a real behavior change, not just an implementation swap.

## Recommended path — don't do this all at once

1. **First: extract the `StoreBackend` protocol**, with `InMemoryBackend` as the only implementation initially — this is a pure refactor, zero behavior change, but it's what makes everything after this possible without a bigger rewrite later. Worth doing even before you're ready to touch Redis.
2. **Then: add `RedisBackend`** implementing the same protocol, config-selectable (env var or constructor arg — `Stores(backend="redis", redis_url=...)` vs default in-memory), so small single-process deployments (your current target, per earlier in this conversation) keep working with zero new infra requirement, and people who need multi-worker scale opt in explicitly.
3. **`SessionStore` migrates first, `GlobalStore` second** — session data is the one actually *required* for multi-worker correctness (a user's login state must be visible regardless of which worker handles their next request); `GlobalStore` is more app-specific in how it's used and can reasonably stay in-memory-only for longer if an app's `GlobalStore` usage is read-heavy/rarely-written config rather than something requiring cross-worker consistency.
4. **Keep `redis-py`'s connection pooling in mind** — one `Redis` client instance, shared across the process (not one per request), same principle as any DB connection pool.

## The honest tradeoff to flag to your users

Once Redis is in the picture, `transaction()`'s optimistic-retry semantics are worth surfacing directly in docs: under contention, a Redis-backed `transaction()` block might run its body *more than once* (retry after a `WATCH` conflict) — so the body must be side-effect-free except through the store itself (no `print()`-as-audit-log, no calling an external API inside the block) — a constraint your current in-memory `RLock` version doesn't have, since that one only ever runs the block once, blocking rather than retrying.

Want me to sketch the `StoreBackend` protocol extraction as a concrete diff against your current `stores.py` first, since that's the prerequisite step regardless of which backend you add after?
