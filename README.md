[![PyPI version](https://badge.fury.io/py/env2dict.svg)](https://pypi.org/project/env2dict/)
[![Downloads](https://pepy.tech/badge/env2dict)](https://pepy.tech/project/env2dict)
[![Downloads](https://pepy.tech/badge/env2dict/month)](https://pepy.tech/project/env2dict)
[![Downloads](https://pepy.tech/badge/env2dict/week)](https://pepy.tech/project/env2dict)

- [Environment to python dictionary parser util](#environment-to-python-dictionary-parser-util)
  - [About](#about)
  - [Syntax](#syntax)
  - [Examples](#examples)
  - [How to use](#how-to-use)
  - [More info](#more-info)


# Environment to python dictionary parser util

```sh
pip install env2dict
```

## About

This small package provides an ability of easy setting/overriding Python variables from environment. It is expected that u will use to override your configuration data without changing configuration files itself, what is especially useful for containers-oriented applications.

## Syntax

To use it, u need to define environment variables matches the pattern: **Prefix***Body***OperationSuffix** where:
* **Prefix** is any word to determine target variables; for instance, `DD` prefix means to use only variables starts with `DD`; can be empty, what means to select all available variables (not recommended) 
* *Body* is the name of the target configuration parameter
* **OperationSuffix** is the one of next available suffixes (by default, but u can change your defaults):
  * `_NUMBER` to convert variable value to integer (environment variables are always strings)
  * `_FLOAT` to convert variable value to float
  * `_FLAG` to convert variable value to `optional[boolean]` at that values:
    *  `1`/`yes`/`Yes`/`True`/`true` equal `true`
    *  `0`/`no`/`No`/`False`/`false` equal `false`
    *  `None`/`null`/`NULL` equal `null`
  * `_LIST` means to parse variable value to string list
  * `_LIST_APPEND` means to parse variable value to string list and append to existing list instead of override
  * `_JSON` means to parse variable value as json string
  * no suffix means that no conversion will be performed, so variable value will stay a string

Moreover, u can put nested dicts values using `__` separator in the environment variable name.

Note also that u can combine these suffixes to perform more complicated transformations.

## Examples

* env variable `DD_S_COUNT_NUMBER=10` will be converted to `S_COUNT=10` Python object
* `DD_S_COUNT=10` 🠚 `S_COUNT="10"`
* `DD_USE_THIS_FLAG=yes` 🠚 `USE_THIS=True`
* `DD_USE_THIS_FLAG=true` 🠚 `USE_THIS=True`
* `DD_USE_THIS_FLAG=no` 🠚 `USE_THIS=False`
* `DD_ALLOWED_HOSTS_LIST_APPEND=127.0.0.1;dev.ocr.com;dev.web.com` will append a list `['127.0.0.1', 'dev.ocr.com', 'dev.web.com']` to `ALLOWED_HOSTS` variable
* `DD_READ_ME_JSON={\"a\": 1, \"b\": [1, 2]}` will be translated to `READ_ME={'a': 1, 'b': [1, 2]}`
* `DD_SOME_DICT__KEY1__KEY2=postgres` will create a dictionary `SOME_DICT={'KEY1': {'KEY2': 'postgres'}}` if it doesn't exist and will add a field in existing dictionary by aforementioned route
* `DD_A__B_LIST_APPEND_JSON=[1, 2, 3, [1, 2, \"3\"]]` will append `[1, 2, 3, [1, 2, "3"]]` to the end of value `V` from `A={"B": V}`

## How to use

```python
from env2dict import parse_vars

new_vars = parse_vars(
    prefix='DD_',
    initial_vars=None,
    source=None
)
```

## More info

Please take a look at: 
* `parse_vars` function docstring
* `tests` directory of this package repo.

