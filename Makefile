all:
	@clear
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
	rm -f PASS/1.csv FAIL/1.csv Similar.log Good.csv Fail.csv
