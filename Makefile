.PHONY: docs
docs:
	cd docs/sphinx/; make clean; make html
	rm -rf docs/html
	cp -r docs/sphinx/build/html docs/html

