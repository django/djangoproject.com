# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Entry.summary_html'
        db.add_column('blog_entries', 'summary_html', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Entry.body_html'
        db.add_column('blog_entries', 'body_html', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Entry.summary_html'
        db.delete_column('blog_entries', 'summary_html')

        # Deleting field 'Entry.body_html'
        db.delete_column('blog_entries', 'body_html')


    models = {
        'blog.entry': {
            'Meta': {'ordering': "('-pub_date',)", 'object_name': 'Entry', 'db_table': "'blog_entries'"},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'body_html': ('django.db.models.fields.TextField', [], {}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'summary_html': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['blog']
