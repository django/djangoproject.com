# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for entry in orm['blog.Entry'].objects.all():
            entry.summary_html = entry.summary
            entry.body_html = entry.body
            entry.save()

    def backwards(self, orm):
        "Write your backwards methods here."


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
