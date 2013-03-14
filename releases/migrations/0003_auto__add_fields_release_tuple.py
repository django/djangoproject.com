# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Release.major'
        db.add_column(u'releases_release', 'major',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Release.minor'
        db.add_column(u'releases_release', 'minor',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Release.micro'
        db.add_column(u'releases_release', 'micro',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Release.status'
        db.add_column(u'releases_release', 'status',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1),
                      keep_default=False)

        # Adding field 'Release.iteration'
        db.add_column(u'releases_release', 'iteration',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'Release.date'
        db.alter_column(u'releases_release', 'date', self.gf('django.db.models.fields.DateField')())

    def backwards(self, orm):
        # Deleting field 'Release.major'
        db.delete_column(u'releases_release', 'major')

        # Deleting field 'Release.minor'
        db.delete_column(u'releases_release', 'minor')

        # Deleting field 'Release.micro'
        db.delete_column(u'releases_release', 'micro')

        # Deleting field 'Release.status'
        db.delete_column(u'releases_release', 'status')

        # Deleting field 'Release.iteration'
        db.delete_column(u'releases_release', 'iteration')


        # Changing field 'Release.date'
        db.alter_column(u'releases_release', 'date', self.gf('django.db.models.fields.DateField')(auto_now_add=True))

    models = {
        u'releases.release': {
            'Meta': {'object_name': 'Release'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'iteration': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'major': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'micro': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'minor': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'})
        }
    }

    complete_apps = ['releases']
