#.PHONY: sphinx
#sphinx:
#	cd docs/sphinx/; make clean; make html
#	rm -rf slrg_data_collection/docs/html
#	cp -r docs/sphinx/build/html slrg_data_collection/docs/html

#.PHONY: reports
#reports:
#	cd docs/reports/; xelatex *.tex; xelatex *.tex
#	cp docs/reports/*.pdf docs/sphinx/source/_static/
#	cp docs/reports/*.pdf slrg_data_collection/docs/reports/
#	rm -rf texput.log

#.PHONY: docs
#docs: reports sphinx
