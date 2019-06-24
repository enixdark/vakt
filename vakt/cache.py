"""
Caching mechanisms for vakt
"""

from functools import lru_cache


class EnfoldCache:
    """
    Wraps all underlying storage interface calls with a cache that is represented by another storage.
    When `init` arg is True populates cache with all the existing policies at the startup.
    Typical usage might be:
    storage = EnfoldCache(MongoStorage(...), cache=MemoryStorage(), init=True).
    """

    def __init__(self, storage, cache, init=False):
        self.storage = storage
        self.cache = cache
        if init:
            limit = 1000
            offset = 0
            while True:
                policies = self.storage.get_all(limit, offset)
                if not policies:
                    break
                for p in policies:
                    self.cache.add(p)
                offset = limit + 1

    def add(self, policy):
        """
        Cache storage `add`
        """
        # we aren't catching any exceptions - just letting them pass
        self.storage.add(policy)
        self.cache.add(policy)

    def get(self, uid):
        """
        Cache storage `get`
        """
        policy = self.cache.get(uid)
        if policy:
            return policy
        return self.storage.get(uid)

    def get_all(self, limit, offset):
        """
        Cache storage `get_all`
        """
        result = self.cache.get_all(limit, offset)
        if result:
            return result
        return self.storage.get_all(limit, offset)

    def find_for_inquiry(self, inquiry, checker=None):
        """
        Cache storage `find_for_inquiry`
        """
        result = self.cache.find_for_inquiry(inquiry, checker)
        if result:
            return result
        return self.storage.find_for_inquiry(inquiry, checker)

    def update(self, policy):
        """
        Cache storage `update`
        """
        self.storage.update(policy)
        self.cache.update(policy)

    def delete(self, uid):
        """
        Cache storage `delete`
        """
        self.storage.delete(uid)
        self.cache.delete(uid)


class GuardCache:
    """
    Caches hits of `find_for_inquiry` for given Inquiry and Checker.
    In case of a cache hit returns the cached boolean result, in case of a cache miss goes to a Storage and
    and memorizes its result for future calls with the same Inquiry and Checker.
    If underlying Storage notifies it that policies set has anyhow changed, invalidates all the cached results.
    """

    def __init__(self, storage, maxsize=1024):
        self.storage = storage
        self.stale = True
        self.cache = lru_cache(maxsize)(self.storage.find_for_inquiry)

    def get(self, inquiry, checker):
        if not self.stale:
            return self.cache(inquiry, checker)
        return False

#    def _hash(inquiry, checker):
#        return inquiry.to_json() + type(checker)