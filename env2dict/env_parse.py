"""
source: https://github.com/PasaOpasen/py-env-parser
"""

from typing import Optional, Dict, Any, Sequence

import os
import json
import copy


#region CUSTOM EXCEPTIONS

class ListAppendException(Exception):
    pass


class BreakingRouteException(ListAppendException):
    pass


class NoListAppendToException(ListAppendException):
    pass


class TargetListTypeError(ListAppendException):
    pass


class InputListTypeError(ListAppendException):
    pass

#endregion


#region UTILS

def _put_to_nested_dict(
    dct: Dict[str, Any],
    route: Sequence[str],
    value: Any,
    list_append: bool = False
):
    """
    puts key-value pair in the nested dict
    Args:
        dct:
        route: keys route to the value in the dictionary
        value:
        list_append: if True, checks whether the initial value exists and appends current value to it

    >>> d = {}
    >>> _put_to_nested_dict(d, route=('a', 'b', 'c'), value=1)
    >>> d
    {'a': {'b': {'c': 1}}}
    >>> try:
    ...     _put_to_nested_dict(d, route=('b', 'e'), value=1, list_append=True)
    ... except BreakingRouteException: pass
    >>> try:
    ...     _put_to_nested_dict(d, route=('a', 'b', 'e'), value=1, list_append=True)
    ... except NoListAppendToException: pass
    >>> _put_to_nested_dict(d, route=('a', 'b', 'e'), value='just init')
    >>> try:
    ...     _put_to_nested_dict(d, route=('a', 'b', 'e'), value=1, list_append=True)
    ... except TargetListTypeError: pass
    >>> _put_to_nested_dict(d, route=('a', 'b', 'e'), value=['just init'])
    >>> try:
    ...     _put_to_nested_dict(d, route=('a', 'b', 'e'), value=1, list_append=True)
    ... except InputListTypeError: pass
    >>> _put_to_nested_dict(d, route=('a', 'b', 'e'), value=[1], list_append=True)
    >>> d
    {'a': {'b': {'c': 1, 'e': ['just init', 1]}}}
    """

    assert route

    k = route[0]

    if len(route) == 1:
        if list_append:
            if k not in dct:
                raise NoListAppendToException('no initial list append to')
            lst = dct[k]
            if not isinstance(lst, list):
                raise TargetListTypeError(
                    f'initial list append to -- is exactly {type(lst).__qualname__}, not list'
                )
            if not isinstance(value, list):
                raise InputListTypeError(
                    f'gotten list to append is {type(value).__qualname__}, not list'
                )
            lst.extend(value)  # append after successful checks
        else:  # usual case
            dct[k] = value

        return

    if k not in dct:
        if list_append:
            raise BreakingRouteException('target dict route breaks, no list append to')
        dct[k] = {}

    _put_to_nested_dict(dct[k], route[1:], value, list_append=list_append)


def _rm_suffix(string: str, suffix: str) -> str:
    """
    >>> _rm_suffix('var_with_suffix', suffix='_with_suffix')
    'var'
    """
    return string[:-len(suffix)]

#endregion


def parse_vars(
    prefix: str,
    source: Optional[Dict[str, str]] = None,
    initial_vars: Optional[Dict[str, Any]] = None,
    suffix_int: str = '_NUMBER',
    suffix_float: str = '_FLOAT',
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
        initial_vars: initial variables (necessary for cases such u need to update existing dictionaries)
        suffix_int: suffix which means to convert variable value to int
        suffix_float: suffix which means to convert variable value to float
        suffix_bool: suffix for bool conversion
        suffix_list: suffix for List[str] conversion
        suffix_list_append: like suffix_list but means appending to existing list instead of rewrite
        suffix_json: suffix for parsing variable value as json string
        list_separator: separator in the list string for suffix_list
        dict_level_separator: separator in the variable name for nested dictionary constructing

    Returns:
        new variables dictionary

    Notes:
        - automatically removes prefix and suffixes from variables names before putting
        - changes initial_vars if received; to not change -- just perform copy.deepcopy before using it in the function

    >>> init_vars = dict(a=1, b=2, c=[1, 2], d=dict(a=1))
    >>> parse_vars(initial_vars=copy.deepcopy(init_vars), source=dict(V_a='2', V_d__e='3'), prefix='V_')
    {'a': '2', 'b': 2, 'c': [1, 2], 'd': {'a': 1, 'e': '3'}}
    >>> parse_vars(initial_vars=copy.deepcopy(init_vars), source=dict(V_a_NUMBER='2', V_d__e='3'), prefix='V_')
    {'a': 2, 'b': 2, 'c': [1, 2], 'd': {'a': 1, 'e': '3'}}
    >>> parse_vars(initial_vars=copy.deepcopy(init_vars), source=dict(V_c_LIST_APPEND="3;4"), prefix='V_')
    {'a': 1, 'b': 2, 'c': [1, 2, '3', '4'], 'd': {'a': 1}}
    """

    result = dict(initial_vars or {})
    to_parse = source if source is not None else dict(os.environ)

    if prefix:
        prefix_len = len(prefix)
        to_parse = {
            k[prefix_len:]: v for k, v in to_parse.items()
            if k.startswith(prefix)
        }

    #
    # first loop with simple transformations
    #
    for k, v in sorted(to_parse.items()):

        k_orig = prefix + k
        v_orig = v

        progress = True
        while progress:  # while it is being converted by simple keys
            if k.endswith(suffix_int):
                k = _rm_suffix(k, suffix_int)
                v = int(v)
            elif k.endswith(suffix_float):
                k = _rm_suffix(k, suffix_float)
                v = float(v)
            elif k.endswith(suffix_list):
                assert list_separator
                k = _rm_suffix(k, suffix_list)
                v = v.split(list_separator)
            elif k.endswith(suffix_bool):
                k = _rm_suffix(k, suffix_bool)
                if v in ('yes', 'Yes', 'YES', 'True', 'true', 'TRUE', '1'):
                    v = True
                elif v in ('no', 'No', 'NO', 'False', 'false', 'FALSE', '0'):
                    v = False
                elif v in ('None', 'null', 'NULL'):
                    v = None
                else:
                    raise ValueError(
                        f"unknown bool-convertible value {v} for variable {prefix}{k}{suffix_bool} "
                        f"({k_orig}={v_orig})"
                    )
            elif k.endswith(suffix_json):
                k = _rm_suffix(k, suffix_json)
                v = json.loads(v)

            else:  # cannot convert further, stop loop
                progress = False

        #
        # more heavy logic
        #
        list_append = k.endswith(suffix_list_append)
        if list_append:
            assert list_separator
            k = _rm_suffix(k, suffix_list_append)
            if isinstance(v, str):
                v = v.split(list_separator)

        route = [k]  # initial route to put the value
        if dict_level_separator:
            route = k.split(dict_level_separator)

        if route and all(route):  # exists but without empty parts
            try:
                _put_to_nested_dict(result, route, v, list_append=list_append)
            except ListAppendException as e:
                e.args = (f"{k_orig}={v_orig}\n{e.args[0]}",)
                raise e

    return result

