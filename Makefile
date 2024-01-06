

doctest:
	venv/bin/python -m pytest --doctest-modules ./env2dict

pytest:
	venv/bin/python -m pytest ./tests/test.py

test: doctest pytest
	

wheel:
	venv/bin/python setup.py develop
	venv/bin/python setup.py sdist
	venv/bin/python setup.py bdist_wheel

wheel-push:
	bash wheel-push.sh

pypi-package: wheel wheel-push


