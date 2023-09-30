from settings import add_autocompletion, remove_autocompletion


def parse_command(command: str, twitch_bot: object):
    match command.split():
        case ["quit"]:
            quit()
        case ["help"]:
            print(
                """This app is meant to automatically relay messages from your in game Minecraft chat to a Twitch chat.
If you need to change some previously set values you can edit the settings.json file or just delete it and restart the app
Commands:
quit:
    quit the app
autocomplete:
    learn about autocompletions
        """
            )
        case ["autocomplete", *args]:
            parse_autocomplete(args, twitch_bot)
        case _:
            print("Unrecognized command, see 'help' for valid commands.")


def parse_autocomplete(args: list[str], twitch_bot: object):
    match args:
        case []:
            print(
                """Add relaying chat message autocompletions. Mainly used for emotes.
Example: send 'omeg' in Minecraft and complete to 'OMEGA' in twitch message
Usage: autocomplete <mc_message> <autocompletion>
Leave the <autocompletion> argument empty to remove an existing autocompletion"""
            )
        case _:
            try:
                twitch_bot.update_autocompletions(
                    add_autocompletion((args[0], args[1]))
                )
                print(f"Added autocompletion '{args[0]}': '{args[1]}'")
            except:
                twitch_bot.update_autocompletions(remove_autocompletion(args[0]))
                print(f"Removed autocompletion for {args[0]}")
