.PHONY: sphinx
sphinx:
	cd docs/sphinx/; make clean; make html
	rm -rf docs/html
	cp -r docs/sphinx/build/html docs/html

.PHONY: reports
reports:
	cd docs/reports/; xelatex technical_report.tex; bibtex technical_report; xelatex technical_report.tex; xelatex technical_report.tex
	cp docs/reports/*.pdf docs/sphinx/source/_static/
	rm -rf texput.log

.PHONY: docs
docs: reports sphinx
