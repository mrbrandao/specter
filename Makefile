SHELL=/bin/bash
INSTALL_DIR="$(HOME)/bin"
FILES="crateparse"
FILES+="getcrate"

install:
	@(for i in $(FILES);do \
		install -v $$i $(INSTALL_DIR) ;\
	done)
