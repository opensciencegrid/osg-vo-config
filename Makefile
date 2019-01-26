
ALL = voms-mapfile-default grid-vorolemap

all: $(ALL)

voms-mapfile-default: bin/gen-voms-mapfile
	bin/gen-voms-mapfile > voms-mapfile-default

grid-vorolemap: voms-mapfile-default bin/gen-grid-vorolemap
	bin/gen-grid-vorolemap voms-mapfile-default > grid-vorolemap

clean:
	$(RM) $(ALL)

.PHONY: all clean

