# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Release.date'
        db.alter_column(u'releases_release', 'date', self.gf('django.db.models.fields.DateField')())

    def backwards(self, orm):

        # Changing field 'Release.date'
        db.alter_column(u'releases_release', 'date', self.gf('django.db.models.fields.DateField')(null=True))

    models = {
        u'releases.release': {
            'Meta': {'object_name': 'Release'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'})
        }
    }

    complete_apps = ['releases']
