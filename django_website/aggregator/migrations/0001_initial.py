# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FeedType'
        db.create_table('aggregator_feedtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=250, db_index=True)),
            ('can_self_add', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('aggregator', ['FeedType'])

        # Adding model 'Feed'
        db.create_table('aggregator_feeds', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('feed_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=500)),
            ('public_url', self.gf('django.db.models.fields.URLField')(max_length=500)),
            ('is_defunct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feed_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aggregator.FeedType'])),
        ))
        db.send_create_signal('aggregator', ['Feed'])

        # Adding model 'FeedItem'
        db.create_table('aggregator_feeditems', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aggregator.Feed'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=500)),
            ('summary', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=500, db_index=True)),
        ))
        db.send_create_signal('aggregator', ['FeedItem'])


    def backwards(self, orm):
        
        # Deleting model 'FeedType'
        db.delete_table('aggregator_feedtype')

        # Deleting model 'Feed'
        db.delete_table('aggregator_feeds')

        # Deleting model 'FeedItem'
        db.delete_table('aggregator_feeditems')


    models = {
        'aggregator.feed': {
            'Meta': {'object_name': 'Feed', 'db_table': "'aggregator_feeds'"},
            'feed_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aggregator.FeedType']"}),
            'feed_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_defunct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_url': ('django.db.models.fields.URLField', [], {'max_length': '500'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'aggregator.feeditem': {
            'Meta': {'ordering': "('-date_modified',)", 'object_name': 'FeedItem', 'db_table': "'aggregator_feeditems'"},
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
