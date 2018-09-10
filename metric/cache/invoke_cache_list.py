
class InvokeCacheList:
    def __init__(self):
        self.invoked_cache_list = []

    def index(self, args, kwargs):
        for index, cache in enumerate(self.invoked_cache_list):
            if cache[0] == args and cache[1] == kwargs:
                return index
        return None

    def append(self, args, kwargs, data):
        self.invoked_cache_list.append((args, kwargs, data))

    def __getitem__(self, key):
        for cache in self.invoked_cache_list:
            if key[0] == cache[0] and key[1] == cache[1]:
                return cache[2]
        raise KeyError()

    def __setitem__(self, key, value):
        self.invoked_cache_list.append((key[0], key[1], value))

    def __iter__(self):
        for cache in self.invoked_cache_list:
            yield cache[:2]
