"""
source: https://github.com/PasaOpasen/py-env-parser
"""

from typing import Optional, Dict, Any, Sequence

import os
import json
import copy


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
    initial_vars: Optional[Dict[str, Any]] = None,
    suffix_int: str = '_NUMBER',
    suffix_bool: str = '_FLAG',
    suffix_list: str = '_LIST',
    suffix_list_append: str = '_LIST_APPEND',
    suffix_json: str = '_JSON',
    list_separator: str = ';',
    dict_level_separator: str = '__'
) -> Dict[str, Any]:
    """
    parses variable from str->str dictionary according to name rules
    Args:
        prefix: variables prefixes to select, empty means to select all variables
        source: variable source dict, None means environ
        initial_vars: initial variables
        suffix_int: suffix which means to convert variable value to int
        suffix_bool: suffix for bool conversion
        suffix_list: suffix for List[str] conversion
        suffix_list_append: like suffix_list but means appending to existing list instead of rewrite
        suffix_json: suffix for parsing variable value as json string
        list_separator: separator in the list string for suffix_list
        dict_level_separator: separator in the variable name for nested dictionary constructing

    Returns:
        new variables dictionary

    Notes:
        automatically removes prefix and suffixes from variables names

    >>> init_vars = dict(a=1, b=2, c=[1, 2], d=dict(a=1))
    >>> parse_vars(initial_vars=init_vars, source=dict(V_a='2', V_d__e='3'), prefix='V_')
    {'a': '2', 'b': 2, 'c': [1, 2], 'd': {'a': 1, 'e': '3'}}
    >>> parse_vars(initial_vars=init_vars, source=dict(V_a_NUMBER='2', V_d__e='3'), prefix='V_')
    {'a': 2, 'b': 2, 'c': [1, 2], 'd': {'a': 1, 'e': '3'}}
    >>> parse_vars(initial_vars=init_vars, source=dict(V_c_LIST_APPEND="3;4"), prefix='V_')
    {'a': 1, 'b': 2, 'c': [1, 2, '3', '4'], 'd': {'a': 1}}
    """

    result = copy.deepcopy(initial_vars or {})
    to_parse = source if source is not None else dict(os.environ)

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

        elif k.endswith(suffix_list_append):
            assert list_separator
            k = _rm_suffix(k, suffix_list_append)
            result[k] = (result[k] or []) + v.split(';')
            continue

        result[k] = v

    if dict_level_separator:
        for k, v in sorted(result.items()):
            route = k.split(dict_level_separator)
            if len(route) > 1:
                _put_to_nested_dict(result, route, v)
                result.pop(k)

    return result

