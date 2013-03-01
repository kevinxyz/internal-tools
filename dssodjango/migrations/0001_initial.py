# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SSOAuthInfo'
        db.create_table('dssodjango_ssoauthinfo', (
            ('created_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True, db_column='pk_authinfo_id')),
            ('auth_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, db_index=True)),
            ('browser', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('cn', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('displayName', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('mail', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('objectSid', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('services', self.gf('django.db.models.fields.CharField')(max_length=4096)),
            ('last_service', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('dssodjango', ['SSOAuthInfo'])

        # Adding model 'SSOAppToken'
        db.create_table('dssodjango_ssoapptoken', (
            ('created_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now=True, blank=True)),
            ('token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=48, primary_key=True, db_index=True)),
            ('service', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('ssoauthinfo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dssodjango.SSOAuthInfo'], db_column='fk_ssoauthinfo_id')),
        ))
        db.send_create_signal('dssodjango', ['SSOAppToken'])

        # Adding model 'AppAuthInfo'
        db.create_table('dssodjango_appauthinfo', (
            ('created_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now=True, blank=True)),
            ('app_auth_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, primary_key=True, db_index=True)),
            ('cn', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('displayName', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('mail', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('objectSid', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('dssodjango', ['AppAuthInfo'])

        # Adding model 'URL'
        db.create_table('dssodjango_url', (
            ('created_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True, db_column='pk_url_id')),
            ('short_url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80, db_index=True)),
            ('long_url', self.gf('django.db.models.fields.CharField')(max_length=8192, db_index=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=48, db_index=True)),
            ('total_clicks', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('last_month_clicks', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('decayed_clicks', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('dssodjango', ['URL'])

        # Adding model 'LDAPUser'
        db.create_table('dssodjango_ldapuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('dssodjango.models.NowDateTimeField')(auto_now=True, blank=True)),
            ('cn', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256, db_index=True)),
            ('displayName', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('mail', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='direct_reports', null=True, to=orm['dssodjango.LDAPUser'])),
            ('address', self.gf('django.db.models.fields.CharField')(default='', max_length=120, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default='', max_length=120, blank=True)),
            ('department', self.gf('django.db.models.fields.CharField')(default='', max_length=120, db_index=True, blank=True)),
            ('hire_date', self.gf('dssodjango.models.NowDateTimeField')(db_index=True, blank=True)),
            ('ldap_username', self.gf('django.db.models.fields.CharField')(default='', max_length=120, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(default='', max_length=120, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='', max_length=2, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=120, db_index=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(default='', max_length=12, blank=True)),
        ))
        db.send_create_signal('dssodjango', ['LDAPUser'])


    def backwards(self, orm):
        # Deleting model 'SSOAuthInfo'
        db.delete_table('dssodjango_ssoauthinfo')

        # Deleting model 'SSOAppToken'
        db.delete_table('dssodjango_ssoapptoken')

        # Deleting model 'AppAuthInfo'
        db.delete_table('dssodjango_appauthinfo')

        # Deleting model 'URL'
        db.delete_table('dssodjango_url')

        # Deleting model 'LDAPUser'
        db.delete_table('dssodjango_ldapuser')


    models = {
        'dssodjango.appauthinfo': {
            'Meta': {'object_name': 'AppAuthInfo'},
            'app_auth_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'primary_key': 'True', 'db_index': 'True'}),
            'cn': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'created_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'displayName': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'mail': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'objectSid': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dssodjango.ldapuser': {
            'Meta': {'object_name': 'LDAPUser'},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '120', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '120', 'blank': 'True'}),
            'cn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256', 'db_index': 'True'}),
            'created_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '120', 'db_index': 'True', 'blank': 'True'}),
            'displayName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'hire_date': ('dssodjango.models.NowDateTimeField', [], {'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ldap_username': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '120', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '120', 'blank': 'True'}),
            'mail': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'direct_reports'", 'null': 'True', 'to': "orm['dssodjango.LDAPUser']"}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '120', 'db_index': 'True', 'blank': 'True'}),
            'updated_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12', 'blank': 'True'})
        },
        'dssodjango.ssoapptoken': {
            'Meta': {'object_name': 'SSOAppToken'},
            'created_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'ssoauthinfo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dssodjango.SSOAuthInfo']", 'db_column': "'fk_ssoauthinfo_id'"}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '48', 'primary_key': 'True', 'db_index': 'True'}),
            'updated_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dssodjango.ssoauthinfo': {
            'Meta': {'object_name': 'SSOAuthInfo'},
            'auth_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            'browser': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'cn': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'created_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'displayName': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "'pk_authinfo_id'"}),
            'last_service': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'mail': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'objectSid': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'services': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'updated_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dssodjango.url': {
            'Meta': {'object_name': 'URL'},
            'created_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'decayed_clicks': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "'pk_url_id'"}),
            'last_month_clicks': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'long_url': ('django.db.models.fields.CharField', [], {'max_length': '8192', 'db_index': 'True'}),
            'short_url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80', 'db_index': 'True'}),
            'total_clicks': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'updated_at': ('dssodjango.models.NowDateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '48', 'db_index': 'True'})
        }
    }

    complete_apps = ['dssodjango']