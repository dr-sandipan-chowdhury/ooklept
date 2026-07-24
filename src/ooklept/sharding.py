# ooklept/sharding.py

import hashlib


def shard_index(key: str, num_shards: int) -> int:
    """
    Deterministically map a string key to a shard number in [0, num_shards).

    Uses hashlib (not the built-in hash()) because Python's hash() is
    randomized per-process for strings — the same key would map to a
    different shard on every server restart, silently scattering data
    that used to belong to one shard across others over time.
    """
    digest = hashlib.md5(key.encode()).hexdigest()
    return int(digest, 16) % num_shards
