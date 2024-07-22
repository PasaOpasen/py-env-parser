

doctest:
	venv/bin/python -m pytest --doctest-modules ./env2dict

pytest:
	venv/bin/python -m pytest ./tests/test.py

test: doctest pytest


