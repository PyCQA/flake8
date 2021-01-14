"""Cache files manager"""
import hashlib
import os
import pickle


class Cacher(object):
    def __init__(self, file_name, cache_path):
        # type: (str, str) -> None
        self.file_name = file_name
        enc = hashlib.md5(file_name.encode())
        self.cache_path = os.path.join(cache_path, str(enc.hexdigest()))

    def get(self):
        if not os.path.exists(self.cache_path):
            return
        with open(self.cache_path, "rb") as fr:
            mtime, results = pickle.load(fr)
            # if the mtime doesn't change then return cache.
            # otherwise it is invalid
            current_mtime = os.path.getmtime(self.file_name)
            if mtime == current_mtime:
                return results

    def save(self, results):
        """saves the given result to the cache file"""
        with open(self.cache_path, "wb") as fw:
            current_mtime = os.path.getmtime(self.file_name)
            pickle.dump((current_mtime, results), fw)
