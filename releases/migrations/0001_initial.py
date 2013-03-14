# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Release'
        db.create_table(u'releases_release', (
            ('version', self.gf('django.db.models.fields.CharField')(max_length=16, primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal(u'releases', ['Release'])


    def backwards(self, orm):
        # Deleting model 'Release'
        db.delete_table(u'releases_release')


    models = {
        u'releases.release': {
            'Meta': {'object_name': 'Release'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'})
        }
    }

    complete_apps = ['releases']