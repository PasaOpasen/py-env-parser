

doctest:
	venv/bin/python -m pytest --doctest-modules ./env_parse.py


test: doctest
	venv/bin/python -m pytest ./test.py


