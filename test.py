
from pathlib import Path
import json

from env_parse import parse_vars


def read_json(path: str):
    return json.loads(
        Path(path).read_text(encoding='utf-8')
    )


def save_json(path: str, content):
    Path(path).write_text(json.dumps(content), encoding='utf-8')


def test():

    inpath = './example_input.json'
    outpath = './example_output.json'

    i = parse_vars(
        prefix='var_',
        source=read_json(inpath)
    )

    assert i == read_json(outpath)


def test_heavy():

    inpath = './example_heavy_input.json'
    outpath = './example_heavy_output.json'
    vars_path = './example_heavy_inits.json'

    i = parse_vars(
        prefix='V_',
        source=read_json(inpath),
        initial_vars=read_json(vars_path)
    )

    assert i == read_json(outpath)


