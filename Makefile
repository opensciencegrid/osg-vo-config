
ALL = grid-vorolemap

all: $(ALL)

grid-vorolemap: bin/gen-grid-vorolemap
	bin/gen-grid-vorolemap voms-mapfile-default > grid-vorolemap

clean:
	$(RM) $(ALL)

.PHONY: all clean

