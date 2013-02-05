# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ICLA'
        db.create_table('cla_icla', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='iclas', null=True, to=orm['auth.User'])),
            ('date_signed', self.gf('django.db.models.fields.DateField')()),
            ('cla', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('mailing_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('cla', ['ICLA'])

        # Adding model 'CCLA'
        db.create_table('cla_ccla', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_signed', self.gf('django.db.models.fields.DateField')()),
            ('cla', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('company_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('contact_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('contact_title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('cla', ['CCLA'])

        # Adding model 'CCLADesignee'
        db.create_table('cla_ccladesignee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ccla', self.gf('django.db.models.fields.related.ForeignKey')(related_name='designees', to=orm['cla.CCLA'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('icla', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['cla.ICLA'])),
            ('date_added', self.gf('django.db.models.fields.DateField')()),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal('cla', ['CCLADesignee'])


    def backwards(self, orm):
        
        # Deleting model 'ICLA'
        db.delete_table('cla_icla')

        # Deleting model 'CCLA'
        db.delete_table('cla_ccla')

        # Deleting model 'CCLADesignee'
        db.delete_table('cla_ccladesignee')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cla.ccla': {
            'Meta': {'object_name': 'CCLA'},
            'cla': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'company_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'contact_title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_signed': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'cla.ccladesignee': {
            'Meta': {'object_name': 'CCLADesignee'},
            'ccla': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'designees'", 'to': "orm['cla.CCLA']"}),
            'date_added': ('django.db.models.fields.DateField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'icla': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['cla.ICLA']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'cla.icla': {
            'Meta': {'object_name': 'ICLA'},
            'cla': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'date_signed': ('django.db.models.fields.DateField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'iclas'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cla']
