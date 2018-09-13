.PHONY: test build install publish

# the library name
name = json-api
# pip version
pip = pip3

clean:
	rm -fr build dist *.egg-info

build: clean
	python2 setup.py bdist_wheel --python-tag py3

install: build
	$(pip) install --force-reinstall ./dist/*.whl

publish: install
	twine upload dist/* && git push --follow-tags

uninstall:
	pip uninstall $(name) -y
	pip3 uninstall $(name) -y
