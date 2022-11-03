"""Implementation of classes that parse configuration files."""
import os
import sys
from functools import reduce
from typing import Optional, Sequence

from cfg_load import Configuration
from cfg_load import load as load_cfg
from yaml import Loader, add_constructor, add_implicit_resolver

from py4ai.config.utils import PathLike, joinPath, path_constructor, path_matcher, union

from . import _version

__version__ = _version.get_versions()["version"]

# register tag handlers
add_implicit_resolver("!path", path_matcher)
add_constructor("!path", path_constructor)
add_constructor("!joinPath", joinPath)


def load_from_file(filename: PathLike) -> Configuration:
    """
    Load configuration reading given filename.

    :param filename: file to read
    :return: loaded configuration
    """
    try:
        return load_cfg(filename, safe_load=False, Loader=Loader)
    except TypeError:
        return load_cfg(filename)


def get_all_configuration_file(
    application_file: PathLike = "application.yml", name_env: str = "CONFIG_FILE"
) -> Sequence[str]:
    """
    Retrieve all configuration files from system path, including the one in environment variable.

    :param application_file: name of the configuration file to retrieve
    :param name_env: environment variable specifying the path to a specific configuration file
    :return: list of retrieved paths
    """
    confs = [
        os.path.join(path, application_file)
        for path in sys.path
        if os.path.exists(os.path.join(path, application_file))
    ]
    env = [] if name_env not in os.environ.keys() else os.environ[name_env].split(":")
    print(f"Using Configuration files: {', '.join(confs + env)}")
    return confs + env


def merge_confs(
    filenames: Sequence[PathLike], default: Optional[str] = "defaults.yml"
) -> Configuration:
    """
    Merge configurations in given files.

    :param filenames: files to merge
    :param default: default configurations
    :return: merged configuration
    """
    lst = [default, *filenames] if default is not None else filenames
    print(f"Using Default Configuration file: {lst[0]}")
    return reduce(
        lambda config, fil: config.update(load_from_file(fil)),
        lst[1:],
        load_from_file(lst[0]),
    )
