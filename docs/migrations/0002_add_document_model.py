# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Document'
        db.create_table('docs_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documents', to=orm['docs.DocumentRelease'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('docs', ['Document'])


    def backwards(self, orm):
        
        # Deleting model 'Document'
        db.delete_table('docs_document')


    models = {
        'docs.document': {
            'Meta': {'object_name': 'Document'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': "orm['docs.DocumentRelease']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
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
