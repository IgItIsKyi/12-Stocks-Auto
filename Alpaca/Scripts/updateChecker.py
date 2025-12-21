import requests
import subprocess
import sys
import os
import json
import re
from pathlib import Path
REPO = "IgItIsKyi/12-Stocks-Auto"
APP_DIR = Path(os.getenv("LOCALAPPDATA")) / "12-Stocks-Auto"
sys.path.insert(0,str(APP_DIR))
from version import __version__


API_URL = "https://api.github.com/repos/" + REPO +"/releases/latest"


def check_for_update():
    try:
        response = requests.get(API_URL, timeout=5).json()
        latest_version = response["tag_name"].lstrip("v")

        if latest_version != __version__:
            return True, latest_version
    except Exception as e:
        print("Exception occured: " + str(e))

    return False, __version__

def getCurrentVersion():
    return __version__