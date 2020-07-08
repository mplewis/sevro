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


with open('conf.yaml') as f:
    raw = yaml.safe_load(f)
    conf = Config(raw)
    conf.validate()

pprint(conf.to_primitive())
