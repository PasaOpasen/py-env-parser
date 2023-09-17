
from pathlib import Path
import json

from env_parse import parse_vars


def read_json(path: str):
    return json.loads(
        Path(path).read_text(encoding='utf-8')
    )


def test():

    inpath = './example_input.json'
    outpath = './example_output.json'

    i = parse_vars(
        prefix='var_',
        source=read_json(inpath)
    )

    assert i == read_json(outpath)




