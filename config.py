import json
import sys

from utils import log
from constants import *


reports_channel_id = None
announcements_channel_id = None
discord_token = None
database_connection_string = None


try:
    with open(config_filename, "r") as f:
        for fn, val in json.load(f).items():
            setattr(sys.modules[__name__], fn, val)

except Exception as e:
    log("Could not load config. ")
