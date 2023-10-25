

doctest:
	venv/bin/python -m pytest --doctest-modules ./env2dict

pytest:
	venv/bin/python -m pytest ./tests/test.py

test: doctest pytest
	

pypipush:
	python setup.py develop
	python setup.py sdist
	python setup.py bdist_wheel
	twine upload dist/* --skip-existing

