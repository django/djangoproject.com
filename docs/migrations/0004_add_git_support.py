# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'DocumentRelease.docs_subdir'
        db.add_column('docs_documentrelease', 'docs_subdir', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True), keep_default=False)

        # Changing field 'DocumentRelease.scm_url'
        db.alter_column('docs_documentrelease', 'scm_url', self.gf('django.db.models.fields.CharField')(max_length=200))


    def backwards(self, orm):
        
        # Deleting field 'DocumentRelease.docs_subdir'
        db.delete_column('docs_documentrelease', 'docs_subdir')

        # Changing field 'DocumentRelease.scm_url'
        db.alter_column('docs_documentrelease', 'scm_url', self.gf('django.db.models.fields.URLField')(max_length=200))


    models = {
        'docs.document': {
            'Meta': {'object_name': 'Document'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': "orm['docs.DocumentRelease']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'docs.documentrelease': {
            'Meta': {'object_name': 'DocumentRelease'},
            'docs_subdir': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'scm': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'scm_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['docs']
