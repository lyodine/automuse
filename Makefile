all: build doc


build-sdist:
	python3 -m build --sdist

build-wheel:
	python3 -m build --wheel

# Build the source code
build:
	python -m build .

# Submit version
submit: build
	twine upload dist/*

# Build documentation
doc:
	bash ./docs/update.bat

# Clear documentation
doc-clear:
	rm ./docs/build/* -r

