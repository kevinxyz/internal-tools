#!/usr/bin/python
"""
Make sure you have done the followings:
sudo apt-get install python-ldap ldap-utils
"""
import argparse
import re
from string import ascii_lowercase
import sys
import base64
import ldap
import ldif
from django.db import transaction, IntegrityError

from configs.settings import ldap as ldap_settings
from dssodjango.models import LDAPUser


def configure_argument_parser(parser=argparse.ArgumentParser()):
    """
    param {argparse.ArgumentParser} parser: a parser that we populate
        specific options.
    """
    parser.add_argument('--save-all',
                        dest='save_all',
                        action='store_true',
                        help='All (A-Z) users save to DB',
                        default=False)
    parser.add_argument('--query',
                        dest='query',
                        action='store',
                        help='Specific query (mail=kevin@*)',
                        default=None)
    return parser


class LDAPPopulator(object):
    """
    LDAP fetcher and DB populater.
    """
    def __init__(self):
        try:
            print "Connecting to ldap://%s:%s" % (ldap_settings.LDAP_SERVER,
                                                  ldap_settings.LDAP_PORT)
            ld = ldap.initialize("ldap://%s:%d" % (ldap_settings.LDAP_SERVER,
                                                   ldap_settings.LDAP_PORT))
            ld.protocol_version = ldap.VERSION3
            username = ldap_settings.LDAP_USERNAME
            password = ldap_settings.LDAP_PASSWORD
            ld.simple_bind_s(username, password)
            #ld.simple_bind(username, password)

        except ldap.LDAPError as e:
            print "Error: %s" % e
            sys.exit(1)
        self.ld = ld
        #ld.unbind()

    @transaction.autocommit
    def fetch_and_write_to_db(self, query='mail=kevin.chang@*'):
        """
        query = 'mail=shuang*@*'
        query = 'mail=richard@*'
        query = 'mail=viral.shah@*'
        query = 'cn=*blago*'
        query = '(&(cn=*Rosenb*)(objectClass=user))'
        query = '(&(cn=A*)(|(objectClass=user)(objectClass=person)))'
        query = "&(cn=A*)(objectCategory=Person)", None)
        """
        results = self.ld.search_s(ldap_settings.LDAP_BASE_DN,
                                   ldap.SCOPE_SUBTREE,
                                   query,
                                   None)
        #ldif_writer = ldif.LDIFWriter(sys.stdout)
        #ldif_writer.unparse(dn, entry)
        info = {}
        for key, entries in results:
            info['CN'] = key
            buffer = ["CN:%s" % info['CN']]
            for key, val in sorted(entries.iteritems()):
                if key in ('objectSid', 'objectGUID'):
                    val = (base64.b64encode(val[0]),)
                elif key == 'whenCreated':
                    # example: 20110815172442.0Z
                    ts = val[0]
                    year = int(ts[:4])
                    month = int(ts[4:6])
                    day = int(ts[6:8]) if len(ts) > 6 else 1
                    hour = int(ts[8:10]) if len(ts) > 8 else 0
                    min = int(ts[10:12]) if len(ts) > 10 else 0
                    sec = int(ts[12:14]) if len(ts) > 12 else 0
                    val = '%.4d-%.2d-%.2d %.2d:%.2d:%.2d' % (
                        year, month, day, hour, min, sec)
                    val = (val,)
                    #datetime.date(year, month, day)
                elif key in ('msExchMailboxSecurityDescriptor',
                             'mSMQSignCertificates'):
                    continue
                buffer.append("\t%s:%s" % (key, val))
                info[key] = val[0]

            if re.search(r'OU=' + ldap_settings.PERSON_REGEX, info['CN']):
                print '\n'.join(buffer)
                self.write_user_info_to_db(info)
            else:
                print "Skipping %s (probably not a person)" % info['CN']

    @transaction.autocommit
    def write_user_info_to_db(self, info):
        #print "INFO:%s" % info
        # make sure the manager exists
        if 'manager' in info:
            manager = self.get_manager(info['manager'])
        else:
            manager = None

        try:
            ldap_user_obj = LDAPUser.objects.get(cn=info['CN'])
            # overwrite
            ldap_user_obj.cn = info['CN']
            ldap_user_obj.displayName = info['displayName']
            ldap_user_obj.mail = info['mail']
            ldap_user_obj.hire_date = info['whenCreated']
            ldap_user_obj.department = info.get('department', '')
            ldap_user_obj.title = info.get('title', '')
            ldap_user_obj.state = info.get('st', '')
            ldap_user_obj.location = info.get('l', '')

            ldap_user_obj.manager = manager

        except LDAPUser.DoesNotExist:
            ldap_user_obj = LDAPUser(
                cn=info['CN'],
                displayName=info['displayName'],
                mail=info['mail'],
                hire_date=info['whenCreated'],
                department=info.get('department', ''),
                title=info.get('title', ''),
                state=info.get('st', ''),
                location=info.get('l', ''),
                manager=manager)

        try:
            print "Saving %s" % info['CN']
            ldap_user_obj.save()
        except IntegrityError as e:
            print "Trying to save:%s" % info
            transaction.rollback()
            raise e

    @transaction.autocommit
    def get_manager(self, manager_cn):
        try:
            manager_obj = LDAPUser.objects.get(cn=manager_cn)
        except LDAPUser.DoesNotExist:
            manager_obj = LDAPUser(
                cn=manager_cn,
                displayName='',
                mail='',
                hire_date='1900-01-01')
            try:
                print "Adding blank manager: %s" % manager_cn
                manager_obj.save()
            except IntegrityError as e:
                print "Trying to save:%s" % info
                transaction.rollback()
                raise e

        return manager_obj

    def _fetch_test(self):
        ldap_result_id = self.ld.search(ldap_settings.LDAP_BASE_DN,
                                        ldap.SCOPE_SUBTREE,
                                        "cn=*", None)
        ldif_writer = ldif.LDIFWriter(sys.stdout)
        count = 0
        while 1:
            result_type, result_data = self.ld.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    count += 1
                    print result_data
                    #result_set.append(result_data)
                else:
                    print "Type:%s" % result_type
        print "Counted:%d" % count

if __name__ == '__main__':
    populator = LDAPPopulator()

    parser = configure_argument_parser()
    options = parser.parse_args(sys.argv[1:])

    if options.save_all:
        for char in ascii_lowercase:
            print "Fetching %s..." % char
            populator.fetch_and_write_to_db('mail=%s*@*' % char)
    elif options.query:
        populator.fetch_and_write_to_db(options.query)

    sys.exit(0)
    info = {
        'CN': 'CN=Annette Bernardino,OU=Contacts,OU=Santa Monica,DC=corp,DC=dm,DC=local',
        'displayName': 'Annette Bernardino',
        'mail': 'abernardino@sbcglobal.net',
        #'objectSid': 'AQUAAAAAAAUVAAAA72K+oNNHJLFfCSkZ5nsAAA==',
        'whenCreated': '2010-6-21 16:48:42',
        'department': 'Content',
        'title': 'Video Producer - Cracked.com',
        }
    populator.write_user_info_to_db(info)
