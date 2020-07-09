from typing import Optional, List

import yaml
from schematics.models import Model
from schematics.types import StringType, DictType, ListType, UnionType


SEVRO_VERSION = "v1"

KeyOption = StringType
KeyValueOption = DictType(StringType)
YoutubeDlOption = UnionType((KeyOption, KeyValueOption))


class Config(Model):
    """The configuration file format for Sevro."""

    sevro = StringType(regex=rf"^{SEVRO_VERSION}$", required=True)
    youtube_dl_options = ListType(YoutubeDlOption)

    channel_format = StringType()
    playlist_format = StringType()
    video_format = StringType()

    channels = DictType(StringType)
    playlists = DictType(StringType)
    videos = ListType(StringType)

    def cli_options(self, extras: Optional[dict] = None) -> List[str]:
        """Parse the provided youtube_dl_options into a list of CLI options strings, including any
        extra overrides from a provided options dict."""
        if not extras:
            extras = {}
        standardized = {**standardize_mixed_options(self.youtube_dl_options), **extras}
        return build_cli_options(standardized)


def read_config(path: str) -> Config:
    """Read and validate the configuration at the specified path."""
    with open(path) as f:
        raw = yaml.safe_load(f)
    conf = Config(raw)
    conf.validate()
    return conf


def hyphenize(key: str, val: Optional[str]) -> (str, bool):
    """
    Turn a single key and value into a CLI option string.
    Use a single hyphen and single space for single-char options.
    Use a double hyphen and single equals for all other options.
    If there's no value, omit the value part.
    """
    if val is None:
        if len(key) == 1:
            return f"-{key}"
        return f"--{key}"

    if len(key) == 1:
        return f"-{key} {val}"
    return f"--{key}={val}"


def build_cli_options(opts: dict) -> List[str]:
    """Convert a dict of CLI options into a CLI option array."""
    return [hyphenize(key, val) for key, val in opts.items()]


def standardize_mixed_options(raw: List[YoutubeDlOption]) -> dict:
    """Turn [YoutubeDlOption] into a simple key-value dict. Valueless keys are set to value None."""
    if raw is None:
        return {}

    opts = {}
    for item in raw:
        if isinstance(item, str):
            opts[item] = None
        else:
            for key, val in item.items():
                opts[key] = val
    return opts


def merge_format(conf: Config, fmt: Optional[str]) -> List[str]:
    """Merge the CLI options from a config with an optional youtube-dl format string."""
    addl = None
    if fmt:
        addl = {"o": fmt}
    return conf.cli_options(addl)
