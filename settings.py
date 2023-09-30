import re
import sys, os
import json


class Setting:
    def __init__(self, name: str, question: str, processing_function=None):
        self.name = name
        self.question = question
        self.processing_function = processing_function

    def get_from_user(self):
        val = input(self.question)
        if self.processing_function is None:
            return val
        else:
            return self.processing_function(val)


def fix_path(path: str) -> str:
    fixed_path = re.sub(r"/+$", "", re.sub(r"\\+", "/", path))
    return fixed_path


def fix_token(token: str) -> str:
    fixed_token = re.sub(r"^(?!oauth:)", "oauth:", token)
    return fixed_token


def get_channels(channels: str) -> list[str]:
    new_channels = channels.split(", ")
    return new_channels


def get_settings():
    settings_path = os.path.join(
        os.path.dirname(os.path.abspath(sys.argv[0])), "settings.json"
    )
    with open(settings_path, "r") as f:
        return json.loads(f.read())


def write_settings(settings):
    settings_path = os.path.join(
        os.path.dirname(os.path.abspath(sys.argv[0])), "settings.json"
    )
    with open(settings_path, "w") as f:
        f.write(json.dumps(settings))


def add_autocompletion(autocompletion: tuple):
    current_settings = get_settings()
    current_settings["Autocompletions"][autocompletion[0]] = autocompletion[1]
    write_settings(current_settings)
    return current_settings["Autocompletions"]


def remove_autocompletion(autocompletion: str):
    current_settings = get_settings()
    try:
        current_settings["Autocompletions"].pop(autocompletion)
    except KeyError:
        return current_settings["Autocompletions"]
    write_settings(current_settings)
    return current_settings["Autocompletions"]


SETTINGS = [
    Setting("MultiMCPath", "Path to your MultiMC folder: ", fix_path),
    Setting(
        "NamingFormat",
        "The naming format for your instances where * is the instance number: ",
    ),
    Setting("Instances", "How many instances would you like to track: "),
    Setting("InGameName", "What is your username in Minecraft: "),
    Setting(
        "OAUTH_TOKEN",
        "Your twitch chat bot oauth token (access token from twitchtokengenerator.com): ",
        fix_token,
    ),
    Setting("BOT_NICK", "Your twitch username: "),
    Setting(
        "CHANNELS",
        "The twitch channels you want the messages relayed to (comma space separated ex. pagman, pogbones, wowee): ",
        get_channels,
    ),
]

OPTIONAL = [
    Setting(
        "Autocompletions",
        "",
    )
]
