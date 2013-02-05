# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DocumentRelease'
        db.create_table('docs_documentrelease', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lang', self.gf('django.db.models.fields.CharField')(default='en', max_length=2)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('scm', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('scm_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('is_default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('docs', ['DocumentRelease'])


    def backwards(self, orm):
        
        # Deleting model 'DocumentRelease'
        db.delete_table('docs_documentrelease')


    models = {
        'docs.documentrelease': {
            'Meta': {'object_name': 'DocumentRelease'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'scm': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'scm_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['docs']
