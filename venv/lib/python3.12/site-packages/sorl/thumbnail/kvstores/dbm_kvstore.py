import os

from sorl.thumbnail.conf import settings
from sorl.thumbnail.kvstores.base import KVStoreBase

try:
    import anydbm as dbm
except KeyError:
    import dbm
except ImportError:
    # Python 3, hopefully
    import dbm

#
# OS filesystem locking primitives.  TODO: Test Windows versions
#
if os.name == 'nt':
    import msvcrt

    def lock(f, readonly):
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

    def unlock(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def lock(f, readonly):
        fcntl.lockf(f.fileno(), fcntl.LOCK_SH if readonly else fcntl.LOCK_EX)

    def unlock(f):
        fcntl.lockf(f.fileno(), fcntl.LOCK_UN)


class DBMContext:
    """
    A context manager to access the key-value store in a concurrent-safe manner.
    """
    __slots__ = ('filename', 'mode', 'readonly', 'lockfile', 'db')

    def __init__(self, filename, mode, readonly):
        self.filename = filename
        self.mode = mode
        self.readonly = readonly
        self.lockfile = open(filename + ".lock", 'w+b')

    def __enter__(self):
        lock(self.lockfile, self.readonly)
        self.db = dbm.open(self.filename, 'c', self.mode)
        return self.db

    def __exit__(self, exval, extype, tb):
        self.db.close()
        unlock(self.lockfile)
        self.lockfile.close()


class KVStore(KVStoreBase):
    # Please note that all the coding effort is devoted to provide correct
    # semantics, not performance.  Therefore, use this store only in development
    # environments.

    def __init__(self):
        super().__init__()
        self.filename = settings.THUMBNAIL_DBM_FILE
        self.mode = settings.THUMBNAIL_DBM_MODE

    def _cast_key(self, key):
        return key if isinstance(key, bytes) else key.encode('utf-8')

    def _get_raw(self, key):
        with DBMContext(self.filename, self.mode, True) as db:
            try:
                return db[self._cast_key(key)]
            except KeyError:
                return None

    def _set_raw(self, key, value):
        with DBMContext(self.filename, self.mode, False) as db:
            db[self._cast_key(key)] = value

    def _delete_raw(self, *keys):
        with DBMContext(self.filename, self.mode, False) as db:
            for key in keys:
                try:
                    del db[self._cast_key(key)]
                except KeyError:
                    pass

    def _find_keys_raw(self, prefix):
        with DBMContext(self.filename, self.mode, True) as db:
            p = self._cast_key(prefix)
            return [k.decode('utf-8') for k in db.keys() if k.startswith(p)]
