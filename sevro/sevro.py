import logging
import subprocess
from os import makedirs, environ
from os.path import join
from typing import List, Optional, Tuple

import colored
import yaml
from pprint import pformat

from schematics.models import Model
from schematics.types import StringType, DictType, ListType, UnionType


SEVRO_VERSION = 'v1'


KeyOption = StringType
KeyValueOption = DictType(StringType)
YoutubeDlOption = UnionType((KeyOption, KeyValueOption))


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(msg)s',
)


def log(msg: str):
    """Log using the default logger at info level."""
    logging.info(msg)


class Config(Model):
    """The configuration file format for Sevro."""
    sevro = StringType(regex=rf'^{SEVRO_VERSION}$', required=True)
    youtube_dl_options = ListType(YoutubeDlOption)

    channel_format = StringType()
    playlist_format = StringType()
    video_format = StringType()

    channels = DictType(StringType)
    playlists = DictType(StringType)
    videos = ListType(StringType)

    def cli_options(self, extras: Optional[dict] = None) -> List[str]:
        if not extras:
            extras = {}
        standardized = {**standardize_mixed_options(self.youtube_dl_options), **extras}
        return build_cli_options(standardized)


def hyphenize(key: str, val: Optional[str]) -> (str, bool):
    """
    Turn a single key and value into a CLI option string.
    Use a single hyphen and single space for single-char options.
    Use a double hyphen and single equals for all other options.
    If there's no value, omit the value part.
    """
    if val is None:
        if len(key) == 1:
            return f'-{key}'
        return f'--{key}'

    if len(key) == 1:
        return f'-{key} {val}'
    return f'--{key}={val}'


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


def read_conf(path: str) -> Config:
    """Read and validate the configuration at the specified path."""
    with open(path) as f:
        raw = yaml.safe_load(f)
    conf = Config(raw)
    conf.validate()
    return conf


def logc(color: str, msg: str):
    """Print a colorized message, resetting the terminal colors at the end."""
    log(color + msg + colored.style.RESET)


def download(target_dir: str, url: str, opts: List[str]):
    """Download stuff from YouTube into the given directory with the specified youtube-dl options."""
    logc(colored.fore.BLUE, f'Downloading to {target_dir}')
    makedirs(target_dir, exist_ok=True)
    cmd = ['youtube-dl', url]
    cmd.extend(opts)
    logc(colored.fore.YELLOW, ' \\\n    '.join(cmd))
    subprocess.call(cmd, cwd=target_dir)


def merge_format(conf: Config, fmt: Optional[str]) -> List[str]:
    """Merge the CLI options from a config with an optional youtube-dl format string."""
    addl = None
    if fmt:
        addl = {'o': fmt}
    return conf.cli_options(addl)


def download_all(
        conf: Config,
        target_dir: str,
        kind: str,
        fmt: Optional[str],
        items: List[Tuple[str, str]],
):
    """Download multiple series of YouTube items into their own named directories."""
    for name, url in items:
        download(join(target_dir, kind, name), url, merge_format(conf, fmt))


def download_playlists(conf: Config, target_dir: str):
    """Download playlists specified in the config."""
    if not conf.playlists:
        return
    download_all(conf, target_dir, 'playlists', conf.playlist_format, conf.playlists.items())


def download_channels(conf: Config, target_dir: str):
    """Download channels specified in the config."""
    if not conf.channels:
        return
    download_all(conf, target_dir, 'channels', conf.channel_format, conf.channels.items())


def download_videos(conf: Config, target_dir: str):
    """Download videos specified in the config."""
    if not conf.videos:
        return
    for url in conf.videos:
        download(join(target_dir, 'videos'), url, merge_format(conf, conf.video_format))


def main():
    config_path = environ['CONFIG_PATH']
    output_dir = environ['OUTPUT_DIR']
    conf = read_conf(config_path)
    log('Starting with the following configuration:')
    log(pformat(conf.to_primitive()))

    download_videos(conf, output_dir)
    download_playlists(conf, output_dir)
    download_channels(conf, output_dir)

    log('Done!')


if __name__ == '__main__':
    main()
