# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Entry'
        db.create_table('blog_entries', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('headline', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('summary', self.gf('django.db.models.fields.TextField')()),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('blog', ['Entry'])


    def backwards(self, orm):
        
        # Deleting model 'Entry'
        db.delete_table('blog_entries')


    models = {
        'blog.entry': {
            'Meta': {'ordering': "('-pub_date',)", 'object_name': 'Entry', 'db_table': "'blog_entries'"},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['blog']
