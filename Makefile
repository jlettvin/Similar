#!/usr/bin/env make

# Similar is intended to always be a submodule for projects that use it.
HOME=..
BANNER=python $(HOME)/Banner/Banner.py -b -t "wr!"

all:
	@clear
	@$(BANNER) "$(MODULE): all"
	@echo "######################### Similar.py ##############################"
	@echo "Similar uses multiple algorithms to detect similarities between"
	@echo "poorly typed data-entry data and their canonical intended values."
	@echo ""
	@echo "It improved one of my client's canonicalization rate from"
	@echo "under 20 percent to over 70 percent"
	@echo ""
	@echo "It is not demonstrated here."
	./Similar.py

.PHONY: clean
clean:
	@$(BANNER) "$(MODULE): clean"
	rm -f PASS/1.csv FAIL/1.csv Similar.log Good.csv Fail.csv
	rm -f *.pep8 *.pyflakes *.pylint

.PHONY: lint
lint: Similar.py
	@$(BANNER) "$(MODULE): lint"
	@-pep8 $< > $<.pep8 2>&1
	@-pylint $< > $<.pylint 2>&1
	@-pyflakes $< > $<.pyflakes 2>&1

