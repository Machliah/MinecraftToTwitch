import os
import re


class Instance:
    def __init__(self, idx: int, settings: dict) -> None:
        self.settings = settings
        self.path = f"{settings['MultiMCPath']}/instances/{settings['NamingFormat']}/.minecraft/logs/latest.log".replace(
            "*", str(idx)
        )
        self.last_time = 0
        self.last_important_line = self.get_line_count()

        if not os.path.isfile(self.path):
            print("File path doesn't exist or isn't a real file. Returning")
            return

    def get_new_chats(self) -> list[str]:
        # print("File update detected, reading data.")
        new_chats = []
        try:
            with open(self.path, "r") as f:
                data = f.readlines()
                for line in range(self.last_important_line + 1, self.get_line_count()):
                    if (
                        f"[Render thread/INFO]: [CHAT] <{self.settings['InGameName']}>"
                        in data[line]
                    ):
                        print(f'{line}: "{data[line].strip()}"')
                        new_chats.append(self.parse_message(data[line]))
                    self.last_important_line = line
        except PermissionError:
            print(
                f"Failed to read file {self.path}, insufficient permission.".format(
                    self.path
                ),
            )
        return new_chats

    def parse_message(self, message: str) -> str:
        return re.sub(f"<.+> ", "", message[40:], 1).strip()

    def get_line_count(self) -> int:
        lines = 0
        with open(self.path, "r") as f:
            while True:
                if not f.readline():
                    break
                lines += 1
        return lines

    def was_modified(self):
        return os.path.getmtime(self.path) <= self.last_time

    def new_lines(self):
        return self.last_important_line < self.get_line_count()
