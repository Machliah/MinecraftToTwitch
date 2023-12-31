import time
import sys, os
import json
import threading
import queue

from bot import TwitchChatBot
from settings import SETTINGS, OPTIONAL
from instance import Instance
from commands import parse_command


def check_settings():
    print(sys.argv[0])
    settings_path = os.path.join(
        os.path.dirname(os.path.abspath(sys.argv[0])), "settings.json"
    )
    if os.path.isfile(settings_path):
        try:
            with open(settings_path, "r") as f:
                return fill_in_missing_settings(json.loads(f.read()))
        except json.decoder.JSONDecodeError:
            os.remove(settings_path)

    return fill_in_missing_settings({})


def fill_in_missing_settings(settings_object):
    settings_path = os.path.join(
        os.path.dirname(os.path.abspath(sys.argv[0])), "settings.json"
    )
    for s in SETTINGS:
        if not s.name in settings_object:
            print(f"Setting {s.name} not found.")
            settings_object[s.name] = s.get_from_user()
    for o in OPTIONAL:
        if not o.name in settings_object:
            settings_object[o.name] = {}
    with open(settings_path, "w") as f:
        f.write(json.dumps(settings_object))
        return settings_object


def monitor_file_for_changes(instance: object, interval: float, callback):
    while True:
        time.sleep(interval)
        now = time.time()
        if instance.was_modified() and instance.new_lines():
            # print(
            #     instance.was_modified(),
            #     instance.new_lines(),
            #     instance.last_important_line,
            #     instance.get_line_count(),
            # )
            for chat in instance.get_new_chats():
                callback(chat)
            instance.last_time = now


def input_loop(message_queue: str):
    while True:
        command = input()
        message_queue.put(command)


def main():
    settings = check_settings()
    message_queue = queue.Queue()
    console_queue = queue.Queue()

    file_checkers = []
    for instance in range(int(settings["Instances"])):
        file_checkers.append(
            threading.Thread(
                target=monitor_file_for_changes,
                args=(
                    Instance(instance + 1, settings),
                    0.25,
                    message_queue.put,
                ),
                daemon=True,
            )
        )
        file_checkers[instance].start()

    twitch_bot = TwitchChatBot(
        settings["OAUTH_TOKEN"],
        settings["BOT_NICK"],
        settings["CHANNELS"],
        settings["Autocompletions"],
    )

    bot_thread = threading.Thread(target=twitch_bot.connect, daemon=True)
    bot_thread.start()

    console_reader = threading.Thread(
        target=input_loop, args=(console_queue,), daemon=True
    )
    console_reader.start()

    idle_ping = 3000
    while True:
        idle_ping -= 1
        if idle_ping == 0:
            twitch_bot.send_command("PING :tmi.twitch.tv")
            idle_ping = 3000

        try:
            twitch_bot.send_chat(message_queue.get_nowait())
        except queue.Empty:
            pass

        while not console_queue.empty():
            try:
                command = console_queue.get_nowait()
                parse_command(command, twitch_bot)
            except queue.Empty:
                break

        time.sleep(0.1)


if __name__ == "__main__":
    main()
