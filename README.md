## VOMS configuration files for OSG

VOMS configuration files used to create vo-package / vo-client RPMS (https://twiki.grid.iu.edu/bin/view/SoftwareTeam/CreateVOClient)

### To rebuild vomsdir from vomses, run

./bin/osg-make-vomsdir --vomses vomses

### To do a consistency check between vomses and vomsdir lsc files, run

./bin/vomses-crosscheck

For more detail on how to make vo-config release, see
> https://twiki.grid.iu.edu/bin/view/Operations/GithubVOPackageUpdate
