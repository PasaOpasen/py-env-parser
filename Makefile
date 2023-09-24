

doctest:
	venv/bin/python -m pytest --doctest-modules ./env_parse.py

pytest:
	venv/bin/python -m pytest ./test.py

test: doctest pytest
	


