dist:
	python3 -m build

.PHONY: clean
clean:
	rm -rf dist

.PHONY: test
test:
	python3 -m unittest tests/*py

.PHONY: upload-test
upload-test: dist
	python3 -m twine upload --repository testpypi dist/*

.PHONY: upload-prod
upload-prod: dist
	python3 -m twine upload dist/*
