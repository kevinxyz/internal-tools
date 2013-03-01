# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'LDAPUser.state'
        db.alter_column('dssodjango_ldapuser', 'state', self.gf('django.db.models.fields.CharField')(max_length=40))

    def backwards(self, orm):

        # Changing field 'LDAPUser.state'
        db.alter_column('dssodjango_ldapuser', 'state', self.gf('django.db.models.fields.CharField')(max_length=2))

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
            'state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
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