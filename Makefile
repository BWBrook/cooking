.PHONY: epub kindle-preflight kindle kindle-store-password kindle-init-config kindle-list

FILE ?=
INCLUDE_RESEARCH ?= 1
KINDLE_ARGS :=

ifeq ($(strip $(INCLUDE_RESEARCH)),1)
KINDLE_ARGS += --include-linked-research
endif

epub:
	python3 scripts/kindle.py epub --file "$(FILE)" $(KINDLE_ARGS)

kindle-preflight:
	python3 scripts/kindle.py kindle-preflight --file "$(FILE)" $(KINDLE_ARGS)

kindle:
	python3 scripts/kindle.py kindle --file "$(FILE)" $(KINDLE_ARGS)

kindle-store-password:
	python3 scripts/kindle.py kindle-store-password

kindle-init-config:
	python3 scripts/kindle.py init-config

kindle-list:
	python3 scripts/kindle.py list
