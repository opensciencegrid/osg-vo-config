#!/usr/bin/python

# output manual mapfile entries from a gums.config + gums db

import os
import re
import sys
import subprocess
import xml.etree.ElementTree as et

if sys.argv[1:]:
    gumsconfig = sys.argv[1]
else:
    gumsconfig = '/etc/gums/gums.config'

xt = et.fromstring(open(gumsconfig).read())


def dictify_elist(elist):
    return dict( (e.get('name'), e) for e in elist )

def sql_escape(s):
    return "'%s'" % s.replace("'", "''")

def sql_list(seq):
    return ', '.join(map(sql_escape, seq))

def run_mysql_query(query):
    #print >>sys.stderr, "running mysql query: %s" % query
    subprocess.call(['mysql', '-u', user, '-p%s' % dbpw, '-h', host,
                     '-P', port, '-BN', dbname, '-e', query])

banned_names = re.split(r', *', xt.get('bannedUserGroups'))

ugs = xt.find('userGroups')
mug_list = ugs.findall('manualUserGroup')
mug_dict = dictify_elist(mug_list)

gtams = xt.find('groupToAccountMappings')
gtam_list = gtams.findall('groupToAccountMapping')
gtam_dict = dictify_elist(gtam_list)

ams = xt.find('accountMappers')
gam_list = ams.findall('groupAccountMapper')
gam_dict = dictify_elist(gam_list)

htgms = xt.find('hostToGroupMappings')
htgm_list = htgms.findall('hostToGroupMapping')
gtam_names = []
for htgm in htgm_list:
    gtam_names += re.split(r', *', htgm.get('groupToAccountMappings'))

hpf = xt.find('persistenceFactories').find('hibernatePersistenceFactory')
user = hpf.get('hibernate.connection.username')
dbpw = hpf.get('hibernate.connection.password')
dburl = hpf.get('hibernate.connection.url')
# 'jdbc:mysql://fermicloud083.fnal.gov:3306/GUMS_1_3'
m = re.search(r'mysql://(.*):(\d+)/(\w+)$', dburl)
host, port, dbname = m.groups()


print "# BANNED"
run_mysql_query("select concat('\"', trim(DN), '\" ', 'banned') from USERS"
                " where GROUP_NAME in (%s)" % sql_list(banned_names))
print

print "# manual mapping table"
run_mysql_query("select concat('\"', trim(DN), '\" ', ACCOUNT) from MAPPING;")
print

print "# manual user groups"
for gtam_name in gtam_names:
    gtam = gtam_dict[gtam_name]
    ug_names = re.split(r', *', gtam.get('userGroups'))
    am_names = re.split(r', *', gtam.get('accountMappers'))

    # just manualUserGroup userGroups
    ug_names = filter(mug_dict.__contains__, ug_names)

    # just groupAccountMapper accountMappers for now (no poolAccountMappers)
    am_names = filter(gam_dict.__contains__, am_names)

    for ug_name in ug_names:
        mug = mug_dict[ug_name]
        mug_name = mug.get('name')
        for am_name in am_names:
            gam = gam_dict[am_name]
            accountName = gam.get('accountName')
            run_mysql_query(
                "select concat('\"', trim(DN), '\" ', %s) from USERS"
                " where GROUP_NAME = %s" % (sql_escape(accountName),
                                            sql_escape(mug_name)))

