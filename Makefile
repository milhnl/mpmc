.POSIX:
.PHONY: install

install:
	cp mpmc.py "${DESTDIR}${PREFIX}/bin/mpmc"
	chmod +x "${DESTDIR}${PREFIX}/bin/mpmc"
