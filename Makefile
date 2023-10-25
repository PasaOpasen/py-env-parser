

doctest:
	venv/bin/python -m pytest --doctest-modules ./env_parse

pytest:
	venv/bin/python -m pytest ./tests/test.py

test: doctest pytest
	


