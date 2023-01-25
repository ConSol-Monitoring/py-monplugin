dist:
	python3 -m build

.PHONY: upload-test
make upload-test: dist
	python3 -m twine upload --repository testpypi dist/*

.PHONY: upload-prod
make upload-prod: dist
	python3 -m twine upload dist/*
