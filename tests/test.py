
import os
from pathlib import Path
import json

from env2dict import parse_vars

_CUR_DIR = os.path.dirname(__file__)


def read_json(path: str):
    return json.loads(
        Path(path).read_text(encoding='utf-8')
    )


def save_json(path: str, content):
    Path(path).write_text(json.dumps(content), encoding='utf-8')


def get_file(name: str) -> str:
    return os.path.join(_CUR_DIR, name)


def test():

    inpath = get_file('example_input.json')
    outpath = get_file('example_output.json')

    i = parse_vars(
        prefix='var_',
        source=read_json(inpath)
    )

    assert i == read_json(outpath)


def test_heavy():

    inpath = get_file('example_heavy_input.json')
    outpath = get_file('example_heavy_output.json')
    vars_path = get_file('example_heavy_inits.json')

    i = parse_vars(
        prefix='V_',
        source=read_json(inpath),
        initial_vars=read_json(vars_path)
    )

    assert i == read_json(outpath)


