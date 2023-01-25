dist:
	python3 -m build

.PHONY: upload-test
upload-test: dist
	python3 -m twine upload --repository testpypi dist/*

.PHONY: upload-prod
upload-prod: dist
	python3 -m twine upload dist/*
