"""Utilities for configuration."""

import os
import re
from collections.abc import Mapping
from copy import deepcopy
from functools import reduce
from typing import Union

from yaml import FullLoader, Loader, Node, SequenceNode, UnsafeLoader

PathLike = Union[str, "os.PathLike[str]"]
path_matcher = re.compile(r"\$\{([^}^{]+)\}")


def path_constructor(
    loader: Union[Loader, FullLoader, UnsafeLoader], node: Node
) -> PathLike:
    """
    Extract the matched value, expand env variable, and replace the match.

    :param loader: not used
    :param node: YAML node
    :return: path
    :raises SyntaxError: if the node value does not match the regex expression for a path-like string
    :raises KeyError: raises an exception if the environment variable is missing
    """
    value = node.value
    match = path_matcher.match(value)

    if match is None:
        raise SyntaxError("Can't match pattern")

    env_var = match.group()[2:-1]
    try:
        return os.environ[env_var] + value[match.end() :]
    except KeyError:
        raise KeyError(
            f"Missing definition of environment variable {env_var} "
            f"needed when parsing configuration file"
        )


def joinPath(loader: Union[Loader, FullLoader, UnsafeLoader], node: Node) -> PathLike:
    """
    Join pieces of a file system path. Can be used as a custom tag handler.

    :param loader: YAML file loader
    :param node: YAML node
    :return: path
    :raises TypeError: if node is not a SequenceNode
    """
    if not isinstance(node, SequenceNode):
        raise TypeError("node input must be a SequenceNode")
    seq = loader.construct_sequence(node)
    return os.path.join(*seq)


def union(*dicts: dict) -> dict:
    """
    Return a dictionary that results from the recursive merge of the input dictionaries.

    :param dicts: list of dicts
    :return: merged dict
    """

    def __dict_merge(dct: dict, merge_dct: dict):
        """
        Recursive dict merge.

        Inspired by :meth:``dict.update()``, instead of updating only top-level keys, dict_merge recurses down into
        dicts nested to an arbitrary depth, updating keys. The ``merge_dct`` is merged into ``dct``.

        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        merged = deepcopy(dct)
        for k, v in merge_dct.items():
            if (
                k in dct
                and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], Mapping)
            ):
                merged[k] = __dict_merge(dct[k], merge_dct[k])
            else:
                merged[k] = merge_dct[k]
        return merged

    return reduce(__dict_merge, dicts)
