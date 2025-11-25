from django.core.cache import InvalidCacheBackendError, cache, caches

from sorl.thumbnail.conf import settings
from sorl.thumbnail.kvstores.base import KVStoreBase
from sorl.thumbnail.models import KVStore as KVStoreModel


class EMPTY_VALUE:
    pass


class KVStore(KVStoreBase):
    _cached_db_kvstore = True

    @property
    def cache(self):
        try:
            kv_cache = caches[settings.THUMBNAIL_CACHE]
        except InvalidCacheBackendError:
            kv_cache = cache
        return kv_cache

    def clear(self, delete_thumbnails=False):
        """
        We can clear the database more efficiently using the prefix here rather
        than calling :meth:`_delete_raw`.
        """
        prefix = settings.THUMBNAIL_KEY_PREFIX
        for key in self._find_keys_raw(prefix):
            self.cache.delete(key)
        KVStoreModel.objects.filter(key__startswith=prefix).delete()
        if delete_thumbnails:
            self.delete_all_thumbnail_files()

    def _get_raw(self, key):
        value = self.cache.get(key)
        if value is None:
            try:
                value = KVStoreModel.objects.get(key=key).value
            except KVStoreModel.DoesNotExist:
                # we set the cache to prevent further db lookups
                value = EMPTY_VALUE
            self.cache.set(key, value, settings.THUMBNAIL_CACHE_TIMEOUT)
        if value == EMPTY_VALUE:
            return None
        return value

    def _set_raw(self, key, value):
        kvstore_value, created = KVStoreModel.objects.get_or_create(
            key=key, defaults={'value': value})
        if not created:
            kvstore_value.value = value
            kvstore_value.save()
        self.cache.set(key, value, settings.THUMBNAIL_CACHE_TIMEOUT)

    def _delete_raw(self, *keys):
        KVStoreModel.objects.filter(key__in=keys).delete()
        for key in keys:
            self.cache.delete(key)

    def _find_keys_raw(self, prefix):
        qs = KVStoreModel.objects.filter(key__startswith=prefix)
        return qs.values_list('key', flat=True)
