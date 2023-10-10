SHELL=/bin/bash
INSTALL_DIR="$(HOME)/bin"
FILES="specter.sh"
FILES+="specter.conf"
FILES+="specrender.py"

uninstall:
	@(for i in $(FILES);do \
		rm -v $(INSTALL_DIR)/$$i ;\
		done)

install:
	@(cd scripts;for i in $(FILES);do \
		install -v $$i $(INSTALL_DIR) ;\
	done)

link:
	@(cd scripts;for i in $(FILES);do \
		file=$$(realpath $$i) ;\
		ln -sv $$file $(INSTALL_DIR) ;\
	done)
