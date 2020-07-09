from pprint import pformat
from os.path import join

from config import read_config
from download import download_videos, download_playlists, download_channels
from logs import setup_logging, log


SEVRO_DIR = "/config"
CONFIG_PATH = join(SEVRO_DIR, "sevro.yaml")
OUTPUT_DIR = "/download"


def main():
    setup_logging()
    conf = read_config(CONFIG_PATH)

    log("Starting with the following configuration:")
    log(pformat(conf.to_primitive()))

    download_videos(conf, OUTPUT_DIR)
    download_playlists(conf, OUTPUT_DIR)
    download_channels(conf, OUTPUT_DIR)

    log("Done!")


if __name__ == "__main__":
    main()
