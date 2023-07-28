SHELL=/bin/bash
INSTALL_DIR="$(HOME)/bin"
FILES="specter"
FILES+="getcrate"
FILES+="vparse.py"

uninstall:
	@(for i in $(FILES);do \
		rm -v $(INSTALL_DIR)/$$i ;\
		done)

install:
	@(for i in $(FILES);do \
		install -v $$i $(INSTALL_DIR) ;\
	done)

link:
	@(for i in $(FILES);do \
		file=$$(realpath $$i) ;\
		ln -sv $$file $(INSTALL_DIR) ;\
	done)
