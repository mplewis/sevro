import subprocess
from os.path import join
from typing import List, Optional, Tuple

from colored import fore

from config import Config, merge_format
from logs import logc
from os import makedirs


def download(target_dir: str, url: str, opts: List[str]):
    """
    Download stuff from YouTube into the given directory with the specified youtube-dl options.
    """
    logc(fore.BLUE, f"Downloading to {target_dir}")
    makedirs(target_dir, exist_ok=True)
    cmd = ["youtube-dl", url]
    cmd.extend(opts)
    logc(fore.YELLOW, " \\\n    ".join(cmd))
    subprocess.call(cmd, cwd=target_dir)


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
    download_all(
        conf, target_dir, "playlists", conf.playlist_format, conf.playlists.items()
    )


def download_channels(conf: Config, target_dir: str):
    """Download channels specified in the config."""
    if not conf.channels:
        return
    download_all(
        conf, target_dir, "channels", conf.channel_format, conf.channels.items()
    )


def download_videos(conf: Config, target_dir: str):
    """Download videos specified in the config."""
    if not conf.videos:
        return
    for url in conf.videos:
        download(join(target_dir, "videos"), url, merge_format(conf, conf.video_format))
