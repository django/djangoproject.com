# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'DocumentRelease', fields ['lang', 'version']
        db.create_unique(u'docs_documentrelease', ['lang', 'version'])

        # Adding unique constraint on 'Document', fields ['release', 'path']
        db.create_unique(u'docs_document', ['release_id', 'path'])


    def backwards(self, orm):
        # Removing unique constraint on 'Document', fields ['release', 'path']
        db.delete_unique(u'docs_document', ['release_id', 'path'])

        # Removing unique constraint on 'DocumentRelease', fields ['lang', 'version']
        db.delete_unique(u'docs_documentrelease', ['lang', 'version'])


    models = {
        u'docs.document': {
            'Meta': {'unique_together': "(('release', 'path'),)", 'object_name': 'Document'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': u"orm['docs.DocumentRelease']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'docs.documentrelease': {
            'Meta': {'unique_together': "(('lang', 'version'),)", 'object_name': 'DocumentRelease'},
            'docs_subdir': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'scm': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'scm_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['docs']