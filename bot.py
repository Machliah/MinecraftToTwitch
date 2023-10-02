import socket


class TwitchChatBot:
    def __init__(
        self, oauth_token: str, username: str, channels: list, autocompletions: dict
    ):
        self.irc_server = "irc.twitch.tv"
        self.irc_port = 6667
        self.oauth_token = oauth_token
        self.username = username
        self.channels = channels
        self.autocompletions = autocompletions

    def send_chat(self, message: str):
        """Send a message to Twitch after replacing autocompletions"""
        new_message = message
        for key, value in self.autocompletions.items():
            new_message = new_message.replace(key, value)
        self.send_privmsg(new_message)

    def update_autocompletions(self, autocompletions: dict):
        self.autocompletions = autocompletions

    def send_privmsg(self, message: str):
        for channel in self.channels:
            self.send_command(f"PRIVMSG #{channel} :{message}")

    def send_command(self, command: str):
        # never print commands with your token in them
        if "PASS" not in command:
            pass
            # print(f"< {command}")
        self.irc.send((command + "\r\n").encode())

    def connect(self):
        """Connect the bot to the given channels"""
        self.irc = socket.socket()
        self.irc.connect((self.irc_server, self.irc_port))
        self.send_command(f"PASS {self.oauth_token}")
        self.send_command(f"NICK {self.username}")
        for channel in self.channels:
            self.send_command(f"JOIN #{channel}")
        # maybe used in the future or during dev, uneeded for actual use
        self.loop_for_messages()

    def handle_message(self, message: str):
        # print(f"> {message}")
        if "PING" in message:
            self.send_command(message.replace("PING", "PONG"))

    def loop_for_messages(self):
        while True:
            received_messages = self.irc.recv(2048).decode()
            for received_message in received_messages.split("\r\n"):
                self.handle_message(received_message)
