# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        # rename tables from the hardcoded old names to the Django defaults.
        db.rename_table('aggregator_feeds', 'aggregator_feed')
        db.rename_table('aggregator_feeditems', 'aggregator_feeditem')

    def backwards(self, orm):
        db.rename_table('aggregator_feed', 'aggregator_feeds')
        db.rename_table('aggregator_feeditem', 'aggregator_feeditems')

    models = {
        'aggregator.feed': {
            'Meta': {'object_name': 'Feed'},
            'feed_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aggregator.FeedType']"}),
            'feed_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_defunct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_url': ('django.db.models.fields.URLField', [], {'max_length': '500'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'aggregator.feeditem': {
            'Meta': {'ordering': "('-date_modified',)", 'object_name': 'FeedItem'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aggregator.Feed']"}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '500'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'aggregator.feedtype': {
            'Meta': {'object_name': 'FeedType'},
            'can_self_add': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '250', 'db_index': 'True'})
        }
    }

    complete_apps = ['aggregator']
