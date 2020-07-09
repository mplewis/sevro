from os import environ
from pprint import pformat

from config import read_config
from download import download_videos, download_playlists, download_channels
from logs import setup_logging, log


def main():
    setup_logging()

    config_path = environ["CONFIG_PATH"]
    output_dir = environ["OUTPUT_DIR"]
    conf = read_config(config_path)

    log("Starting with the following configuration:")
    log(pformat(conf.to_primitive()))

    download_videos(conf, output_dir)
    download_playlists(conf, output_dir)
    download_channels(conf, output_dir)

    log("Done!")


if __name__ == "__main__":
    main()
