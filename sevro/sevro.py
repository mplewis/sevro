from typing import List, Union

import yaml
from pprint import pprint

from schematics.models import Model
from schematics.types import StringType, DictType, ListType, UnionType


KeyOption = StringType
KeyValueOption = DictType(StringType)
YoutubeDlOption = UnionType((KeyOption, KeyValueOption))


class Config(Model):
    sevro = StringType(regex=r'^v1$')
    channels = DictType(StringType)
    playlists = DictType(StringType)
    youtube_dl_options = ListType(YoutubeDlOption)

    def cli_options(self) -> str:
        return build_cli_options(standardize_mixed_options(self.youtube_dl_options))


def hyphenize(key: str) -> str:
    """Hyphenize single-char options with one hyphen, all others with two."""
    if len(key) == 1:
        return f'-{key}'
    return f'--{key}'


def build_cli_options(opts: dict) -> str:
    """Convert a dict of CLI options into a CLI option string."""
    strs = []
    for key, val in opts.items():
        with_hyphen = hyphenize(key)
        if val is None:
            strs.append(with_hyphen)
        else:
            strs.append(f'{with_hyphen}={val}')
    return ' '.join(strs)


def standardize_mixed_options(raw: List[YoutubeDlOption]) -> dict:
    """Turn [YoutubeDlOption] into a simple key-value dict. Valueless keys are set to value None."""
    opts = {}
    for item in raw:
        if isinstance(item, str):
            opts[item] = None
        else:
            for key, val in item.items():
                opts[key] = val
    return opts


with open('conf.yaml') as f:
    raw = yaml.safe_load(f)
    conf = Config(raw)
    conf.validate()

pprint(conf.to_primitive())
pprint(conf.cli_options())
