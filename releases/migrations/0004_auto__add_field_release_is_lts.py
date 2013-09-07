# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Release.is_lts'
        db.add_column(u'releases_release', 'is_lts',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Release.is_lts'
        db.delete_column(u'releases_release', 'is_lts')


    models = {
        u'releases.release': {
            'Meta': {'object_name': 'Release'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'is_lts': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'iteration': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'major': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'micro': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'minor': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'})
        }
    }

    complete_apps = ['releases']