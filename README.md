## VOMS Configuration Files for OSG

### Files Included

-   `vomses`
    This file contains information about VOMS servers, one per line.

    Each line contains 5 fields:
    1.  VO name alias
    2.  Hostname for VOMS server
    3.  Port for VOMS server
    4.  DN for VOMS server certificate
    5.  VO name (should be the same as VO name alias)

-   `vomsdir`
    This directory contains LSC files for each VOMS server,
    with the following layout:

    `vomsdir/<VONAME>/<HOSTNAME>.lsc`

    And each LSC file has two lines: the DN (subject) and CA (issuer)
    for the VOMS server certificate.

-   `voms-mapfile-default`
    This file contains mappings of VOMS FQDN patterns to local user names.


### Adding a VO or VOMS server

To add a new VOMS server, you will need to add a line to the `vomses` file
and a corresponding `.lsc` file, according to the format described above.

If this is a new VO, you will have to create the `vomsdir/<VONAME>` directory
for the `.lsc` file.  Additionally, consult with the new VO to see if any new
VOMS mappings to usernames should be added to `voms-mapfile-default`.


### Adding additional VOMS certificates for an existing VO

The structure of the `vomsdir` only supports a single LSC file per hostname
per VO.  So, in order to add an additional VOMS certificate for an existing
VO, you will have to create an extra hostname (either a new host or just a
hostname alias) for the new VOMS certificate.  Then follow the above
instructions for adding a VOMS server.


### Retiring a VO

To retire a VO, remove any lines in `vomses` for that VO, as well as the
entire `vomsdir/<VONAME>` directory.  Additionally, if there are any VOMS
mappings for the VO in `voms-mapfile-default`, remove those also.


### Tagging a Release

To publish the new release on GitHub:

-   Go to <https://github.com/opensciencegrid/osg-vo-config/releases/new>
-   In the "Tag version" field, enter `release-<NN>` (eg, `release-85`)
-   If you are creating this tag on GitHub, click the "Target" dropdown button,
    and under the "Recent Commits" tab, make sure to select the commit you used
    when creating the tarball (It should be the first one)
-   In the "Release title" field, enter `<MONTH> <YEAR> VO Package Release <NN>`
    (eg, `December 2018 VO Package Release 85`)
-   In the release description, list the changes in this release and their
    associated ticket numbers, similar to the new `%changelog` entry added
    in the rpm spec file

    See <https://github.com/opensciencegrid/osg-vo-config/releases> for examples
-   Click the "Publish release" button


### Miscelaneous

#### To rebuild vomsdir from vomses, run

./bin/osg-make-vomsdir --vomses vomses


#### To do a consistency check between vomses and vomsdir lsc files, run

./bin/vomses-crosscheck


#### For more detail on how to make vo-config release, see

<https://opensciencegrid.org/technology/software/create-vo-client/>


<!--
Don't tell Mom, but if you need them, check out these old twiki pages:

SoftwareTeam/CreateVOClient
Operations/GithubVOPackageUpdate
-->

