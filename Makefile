.PHONY: sphinx
sphinx:
	cd docs/sphinx/; make clean; make html
	rm -rf slrg_data_collection/docs/html
	cp -r docs/sphinx/build/html slrg_data_collection/docs/html

.PHONY: reports
reports:
	cd docs/reports/; xelatex *.tex; xelatex *.tex
	cp slrg_data_collection/docs/report/*.pdf docs/html/_static/
	cp slrg_data_collection/docs/report/*.pdf docs/sphinx/source/_static
	rm -rf texput.log

.PHONY: docs
docs: sphinx reports
