from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from sorl.thumbnail.conf import settings


@python_2_unicode_compatible
class KVStore(models.Model):
    key = models.CharField(
        max_length=200, primary_key=True,
        db_column=settings.THUMBNAIL_KEY_DBCOLUMN
    )
    value = models.TextField()

    def __str__(self):
        return self.key
