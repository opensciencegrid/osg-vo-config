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

def get_vug_pattern(vug):
    name      = vug.get('name')
    voGroup   = vug.get('voGroup')
    role      = vug.get('role')
    matchFQAN = vug.get('matchFQAN')
    vo        = voGroup.split('/')[1]
    voSubGrps = voGroup.split('/', 2)[2:]

    if matchFQAN == 'vo':
        pattern = "/%s/*" % vo
    elif matchFQAN == 'exact':
        if role is None:
            pattern = "%s/Role=NULL/Capability=NULL" % voGroup
        else:
            pattern = "%s/Role=%s/Capability=NULL" % (voGroup, role)

    # currently unused defaults for other matchFQAN values
    elif role is None:
        pattern = "%s/*" % voGroup
    else:
        pattern = "%s/Role=%s/*" % (voGroup, role)

    return pattern

banned_names = re.split(r', *', xt.get('bannedUserGroups'))

ugs = xt.find('userGroups')
mug_list = ugs.findall('manualUserGroup')
mug_dict = dictify_elist(mug_list)

vug_list = ugs.findall('vomsUserGroup')
vug_dict = dictify_elist(vug_list)

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
host, port, dbname = re.search(r'mysql://(.*):(\d+)/(\w+)$', dburl).groups()


print "# Add the following contents to /etc/grid-security/ban-mapfile"
print "# http://opensciencegrid.github.io/docs/security/lcmaps-voms-authentication/#banning-users"
print
run_mysql_query("select concat('\"', trim(DN), '\" ') from USERS"
                " where GROUP_NAME in (%s)" % sql_list(banned_names))
print "# ---"
print

print "# Add the following contents to /etc/grid-security/grid-mapfile"
print "# http://opensciencegrid.github.io/docs/security/lcmaps-voms-authentication/#mapping-users"
print
run_mysql_query("select concat('\"', trim(DN), '\" ', ACCOUNT) from MAPPING;")

current_voms_maps = []
for gtam_name in gtam_names:
    gtam = gtam_dict[gtam_name]
    ug_names = re.split(r', *', gtam.get('userGroups'))
    am_names = re.split(r', *', gtam.get('accountMappers'))

    # just manualUserGroup userGroups
    mug_names = filter(mug_dict.__contains__, ug_names)

    # just vomsUserGroup userGroups
    vug_names = filter(vug_dict.__contains__, ug_names)

    # just groupAccountMapper accountMappers for now (no poolAccountMappers)
    gam_names = filter(gam_dict.__contains__, am_names)

    for gam_name in gam_names:
        gam = gam_dict[gam_name]
        accountName = gam.get('accountName')

        for mug_name in mug_names:
            run_mysql_query(
                "select concat('\"', trim(DN), '\" ', %s) from USERS"
                " where GROUP_NAME = %s" % (sql_escape(accountName),
                                            sql_escape(mug_name)))

        for vug_name in vug_names:
            vug = vug_dict[vug_name]
            pattern = get_vug_pattern(vug)
            current_voms_maps.append((pattern, accountName))
print "# ---"
print


released_voms_maps = [
  ("/cdf/Role=NULL/Capability=NULL", "cdf"),
  ("/cdf/glidecaf/Role=development/Capability=NULL", "cdfdev"),
  ("/cdf/glidecaf/Role=fermigrid/Capability=NULL", "cdffgrid"),
  ("/cdf/glidecaf/Role=namcaf/Capability=NULL", "cdfnam"),
  ("/cdf/glidecaf/Role=testcaf/Capability=NULL", "cdf"),
  ("/fermilab/grid/Role=NULL/Capability=NULL", "fnalgrid"),
  ("/fermilab/accelerator/Role=NULL/Capability=NULL", "fnal_acc"),
  ("/fermilab/coupp/Role=NULL/Capability=NULL", "coupp"),
  ("/fermilab/argoneut/Role=NULL/Capability=NULL", "argoneut"),
  ("/fermilab/cdms/Role=NULL/Capability=NULL", "cdms"),
  ("/fermilab/minerva/Role=NULL/Capability=NULL", "minerva"),
  ("/fermilab/miniboone/Role=NULL/Capability=NULL", "minboone"),
  ("/fermilab/minos/Role=NULL/Capability=NULL", "minos"),
  ("/fermilab/mipp/Role=NULL/Capability=NULL", "mipp"),
  ("/fermilab/mu2e/Role=NULL/Capability=NULL", "mu2e"),
  ("/fermilab/nova/Role=NULL/Capability=NULL", "nova"),
  ("/fermilab/numi/Role=NULL/Capability=NULL", "numi"),
  ("/fermilab/patriot/Role=NULL/Capability=NULL", "patriot"),
  ("/fermilab/theory/Role=NULL/Capability=NULL", "fnal_thy"),
  ("/fermilab/test/Role=NULL/Capability=NULL", "fgtest"),
  ("/fermilab/uboone/Role=NULL/Capability=NULL", "uboone"),
  ("/fermilab/uboone/Role=Production/Capability=NULL", "uboonepro"),
  ("/fermilab/uboone/Role=pilot/Capability=NULL", "uboonegli"),
  ("/fermilab/uboone/Role=Analysis/Capability=NULL", "ubooneana"),
  ("/fermilab/map/Role=NULL/Capability=NULL", "map"),
  ("/fermilab/gm2/Role=NULL/Capability=NULL", "gm2"),
  ("/fermilab/Role=Production/Capability=NULL", "fermipro"),
  ("/fermilab/accelerator/Role=Production/Capability=NULL", "accelpro"),
  ("/fermilab/argoneut/Role=Production/Capability=NULL", "argoneutpro"),
  ("/fermilab/cdms/Role=Production/Capability=NULL", "cdmspro"),
  ("/fermilab/minerva/Role=Production/Capability=NULL", "minervapro"),
  ("/fermilab/miniboone/Role=Production/Capability=NULL", "minbnpro"),
  ("/fermilab/minos/Role=Production/Capability=NULL", "minospro"),
  ("/fermilab/mipp/Role=Production/Capability=NULL", "mipppro"),
  ("/fermilab/nova/Role=Production/Capability=NULL", "novapro"),
  ("/fermilab/numi/Role=Production/Capability=NULL", "numipro"),
  ("/fermilab/patriot/Role=Production/Capability=NULL", "patripro"),
  ("/fermilab/theory/Role=Production/Capability=NULL", "theopro"),
  ("/fermilab/map/Role=Production/Capability=NULL", "mappro"),
  ("/fermilab/gm2/Role=Production/Capability=NULL", "gm2pro"),
  ("/fermilab/argoneut/Role=Analysis/Capability=NULL", "argoneutana"),
  ("/fermilab/minerva/Role=Analysis/Capability=NULL", "minervaana"),
  ("/fermilab/minos/Role=Analysis/Capability=NULL", "minosana"),
  ("/fermilab/nova/Role=Analysis/Capability=NULL", "novaana"),
  ("/fermilab/map/Role=Analysis/Capability=NULL", "mapana"),
  ("/fermilab/gm2/Role=Analysis/Capability=NULL", "gm2ana"),
  ("/fermilab/grid/Role=pilot/Capability=NULL", "fggli"),
  ("/fermilab/argoneut/Role=pilot/Capability=NULL", "argoneutgli"),
  ("/fermilab/minerva/Role=pilot/Capability=NULL", "minervagli"),
  ("/fermilab/minos/Role=pilot/Capability=NULL", "minosgli"),
  ("/fermilab/nova/Role=pilot/Capability=NULL", "novagli"),
  ("/fermilab/map/Role=pilot/Capability=NULL", "mapgli"),
  ("/fermilab/gm2/Role=pilot/Capability=NULL", "gm2gli"),
  ("/fermilab/grid/Role=admin/Capability=NULL", "fgadmin"),
  ("/mis/*", "mis"),
  ("/star/*", "star"),
  ("/cms/uscms/Role=cmst2admin/Capability=NULL", "cmst2admin"),
  ("/cms/uscms/Role=cmssoft/Capability=NULL", "cmssoft"),
  ("/cms/Role=cmssoft/Capability=NULL", "cmssoft"),
  ("/cms/uscms/Role=cmsprod/Capability=NULL", "cmsprod"),
  ("/cms/uscms/Role=cmsphedex/Capability=NULL", "cmsphedex"),
  ("/cms/Role=cmsphedex/Capability=NULL", "cmsphedex"),
  ("/cms/uscms/Role=cmsfrontier/Capability=NULL", "cmsfrontier"),
  ("/cms/Role=production/Capability=NULL", "cmsprod"),
  ("/LIGO/*", "ligo"),
  ("/dzero/users/Role=NULL/Capability=NULL", "samgrid"),
  ("/dzero/users/Role=analysis/Capability=NULL", "dzeroana"),
  ("/dzero/services/Role=NULL/Capability=NULL", "sam"),
  ("/dosar/*", "dosar"),
  ("/des/*", "des"),
  ("/GLOW/*", "glow"),
  ("/nanohub/*", "nanohub"),
  ("/geant4/*", "geant4"),
  ("/geant4/Role=lcgadmin/Capability=NULL", "geant4"),
  ("/i2u2/*", "i2u2"),
  ("/osg/*", "osg"),
  ("/atlas/usatlas/Role=production/Capability=NULL", "usatlas1"),
  ("/atlas/usatlas/Role=software/Capability=NULL", "usatlas2"),
  ("/atlas/*", "usatlas3"),
  ("/atlas/*", "usatlas4"),
  ("/osgedu/*", "osgedu"),
  ("/NWICG/*", "nwicg"),
  ("/ops/*", "ops"),
  ("/des/production/Role=NULL/Capability=NULL", "des"),
  ("/gpn/*", "gpn"),
  ("/CompBioGrid/*", "compbiogrid"),
  ("/Engage/*", "engage"),
  ("/ilc/*", "ilc"),
  ("/NYSGRID/*", "nysgrid"),
  ("/SBGrid/*", "sbgrid"),
  ("/cigi/*", "cigi"),
  ("/icecube/*", "icecube"),
  ("/alice/*", "alice"),
  ("/NEBioGrid/Role=NULL/Capability=NULL", "nebiogrid"),
  ("/Gluex/Role=NULL/Capability=NULL", "gluex"),
  ("/GridUNESP/Role=NULL/Capability=NULL", "gridunesp"),
  ("/dayabay/Role=NULL/Capability=NULL", "dayabay"),
  ("/hcc/Role=NULL/Capability=NULL", "hcc"),
  ("/belle/Role=NULL/Capability=NULL", "belle"),
  ("/CSIU/*", "csiu"),
  ("/suragrid/*", "suragrid"),
  ("/nees/*", "nees"),
  ("/gcvo/*", "gcvo"),
  ("/gcedu/*", "gcedu"),
  ("/superbvo.org/Role=NULL/Capability=NULL", "superbvo.org"),
  ("/superbvo.org/Role=ProductionManager/Capability=NULL", "superbvo.orgprod"),
  ("/superbvo.org/Role=SoftwareManager/Capability=NULL", "superbvo.orgsoft"),
  ("/dream/*", "dream"),
  ("/lbne/Role=NULL/Capability=NULL", "lbne"),
  ("/lbne/Role=Production/Capability=NULL", "lbnepro"),
  ("/lbne/Role=Analysis/Capability=NULL", "lbneana"),
  ("/lbne/Role=pilot/Capability=NULL", "lbnegli"),
  ("/lsst/*", "lsst"),
  ("/UC3/*", "uc3"),
  ("/mcdrd/Role=NULL/Capability=NULL", "mcdrd"),
  ("/lqcd/Role=NULL/Capability=NULL", "lqcd"),
  ("/auger/Role=NULL/Capability=NULL", "auger"),
  ("/glast.org/Role=NULL/Capability=NULL", "glast.org"),
  ("/fermilab/darkside/Role=NULL/Capability=NULL", "darkside"),
  ("/fermilab/darkside/Role=analysis/Capability=NULL", "darksideana"),
  ("/fermilab/darkside/Role=calibration/Capability=NULL", "darksidecal"),
  ("/fermilab/darkside/Role=data/Capability=NULL", "darksidedat"),
  ("/fermilab/grid/Role=pilot/Capability=NULL", "darksidegli"),
  ("/fermilab/darkside/Role=production/Capability=NULL", "darksidepro"),
  ("/nysgrid/*", "nysgrid"),
  ("/belle/Role=production/Capability=NULL", "bellepro"),
  ("/enmr.eu/*", "enmr"),
  ("/osgcrossce/*", "osgcrossce"),
  ("/fermilab/seaquest/Role=NULL/Capability=NULL", "seaquest"),
  ("/fermilab/seaquest/Role=production/Capability=NULL", "seaquestpro"),
  ("/fermilab/seaquest/Role=analysis/Capability=NULL", "seaquestana"),
  ("/fermilab/seaquest/Role=pilot/Capability=NULL", "seaquestgli"),
  ("/enmr.eu/*", "enmr.eu"),
  ("/vo.cta.in2p3.fr/*", "vo.cta.in2p3.fr"),
  ("/xenon.biggrid.nl/*", "xenon.biggrid.nl"),
  ("/fermilab/lariat/Role=NULL/Capability=NULL", "lariat"),
  ("/fermilab/gendetrd/Role=NULL/Capability=NULL", "gendetrd"),
  ("/fermilab/lar1/Role=NULL/Capability=NULL", "lar1"),
  ("/fermilab/okra/Role=NULL/Capability=NULL", "okra"),
  ("/fermilab/lariat/Role=Production/Capability=NULL", "lariatpro"),
  ("/fermilab/gendetrd/Role=Production/Capability=NULL", "gendetrdpro"),
  ("/fermilab/lar1/Role=Production/Capability=NULL", "lar1pro"),
  ("/fermilab/okra/Role=Production/Capability=NULL", "okrapro"),
  ("/fermilab/lariat/Role=Analysis/Capability=NULL", "lariatana"),
  ("/fermilab/gendetrd/Role=Analysis/Capability=NULL", "gendetrdana"),
  ("/fermilab/lar1/Role=Analysis/Capability=NULL", "lar1ana"),
  ("/fermilab/okra/Role=Analysis/Capability=NULL", "okraana"),
  ("/fermilab/lariat/Role=pilot/Capability=NULL", "lariatgli"),
  ("/fermilab/gendetrd/Role=pilot/Capability=NULL", "gendetrdgli"),
  ("/fermilab/lar1/Role=pilot/Capability=NULL", "lar1gli"),
  ("/fermilab/okra/Role=pilot/Capability=NULL", "okragli"),
  ("/snoplus.snolab.ca/*", "snoplus.snolab.ca"),
  ("/fermilab/Role=Analysis/Capability=NULL", "fermiana"),
  ("/fermilab/*", "fnalgrid"),
  ("/LZ/*", "LZ"),
  ("/dune/Role=NULL/Capability=NULL", "dune"),
  ("/dune/Role=Production/Capability=NULL", "dunepro"),
  ("/dune/Role=Analysis/Capability=NULL", "duneana"),
  ("/dune/Role=pilot/Capability=NULL", "dunegli"),
  ("/project8/Role=project8/Capability=NULL", "project8"),
  ("/project8/prod/Role=project8_prod/Capability=NULL", "project8_prod"),
  ("/miniclean/Role=miniclean/Capability=NULL", "miniclean"),
  ("/miniclean/prod/Role=miniclean_prod/Capability=NULL", "miniclean_prod"),
  ("/cdf/Role=Analysis/Capability=NULL", "cdfana"),
  ("/fermilab/Role=pilot/Capability=NULL", "fermigli"),
  ("/cms/Role=pilot/Capability=NULL", "cmspilot"),
  ("/cms/uscms/Role=pilot/Capability=NULL", "uscmslocal"),
  ("/cms/local/Role=pilot/Capability=NULL", "cmslocal"),
  ("/cms/Role=lcgadmin/Capability=NULL", "lcgadmin"),
  ("/dzero/Role=Analysis/Capability=NULL", "dzeroana"),
  ("/des/Role=Analysis/Capability=NULL", "des"),
  ("/osg/ligo/*", "ligo"),
  ("/atlas/usatlas/Role=lcgadmin/Capability=NULL", "usatlas2"),
  ("/atlas/usatlas/*", "usatlas3"),
  ("/CIGI/*", "cigi"),
  ("/cms/*", "cmsuser")
]

custom_voms_maps = set(current_voms_maps) - set(released_voms_maps)

if custom_voms_maps:
    print "# Add the following contents to /etc/grid-security/voms-mapfile"
    print "# http://opensciencegrid.github.io/docs/security/lcmaps-voms-authentication/#mapping-vos"
    print
    # just output never-shipped voms mappings, preserving order found in gums
    for pat_acct in current_voms_maps:
        if pat_acct in custom_voms_maps:
            print '"%s" %s' % pat_acct
    print "# ---"
    print

