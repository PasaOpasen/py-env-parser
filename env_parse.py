
from typing import Optional, Dict, Any, Sequence

import os
import json


def _put_to_nested_dict(dct: Dict[str, Any], route: Sequence[str], value: Any):
    """
    puts key-value pair in the nested dict
    Args:
        dct:
        route: keys route to the value
        value:

    >>> d = {}
    >>> _put_to_nested_dict(d, route=('a', 'b', 'c'), value=1)
    >>> d
    {'a': {'b': {'c': 1}}}
    """

    assert route

    k = route[0]

    if len(route) == 1:
        dct[k] = value
        return

    if k not in dct:
        dct[k] = {}

    _put_to_nested_dict(dct[k], route[1:], value)


def _rm_suffix(string: str, suffix: str) -> str:
    return string[:-len(suffix)]


def parse_vars(
    prefix: str,
    source: Optional[Dict[str, str]] = None,
    suffix_int: str = '_NUMBER',
    suffix_bool: str = '_FLAG',
    suffix_list: str = '_LIST',
    suffix_json: str = '_JSON',
    list_separator: str = ';',
    dict_level_separator: str = '__'
) -> Dict[str, Any]:

    result = {}
    to_parse = source or dict(os.environ)

    if prefix:
        prefix_len = len(prefix)
        to_parse = {
            k[prefix_len:]: v for k, v in to_parse.items()
        }

    #
    # first loop with simple transformations
    #
    for k, v in sorted(to_parse.items()):
        if k.endswith(suffix_int):
            k = _rm_suffix(k, suffix_int)
            v = int(v)
        elif k.endswith(suffix_list):
            assert list_separator
            k = _rm_suffix(k, suffix_list)
            v = v.split(';')
        elif k.endswith(suffix_bool):
            k = _rm_suffix(k, suffix_bool)
            if v in ('yes', 'Yes', 'YES', 'True', 'true', 'TRUE', '1'):
                v = True
            elif v in ('no', 'No', 'NO', 'False', 'false', 'FALSE', '0'):
                v = False
            else:
                raise ValueError(f"unknown bool value {v} for variable {prefix}{k}{suffix_bool}")
        elif k.endswith(suffix_json):
            k = _rm_suffix(k, suffix_json)
            v = json.loads(v)

        result[k] = v

    if dict_level_separator:
        for k, v in sorted(result.items()):
            route = k.split(dict_level_separator)
            if len(route) > 1:
                _put_to_nested_dict(result, route, v)
                result.pop(k)

    return result

