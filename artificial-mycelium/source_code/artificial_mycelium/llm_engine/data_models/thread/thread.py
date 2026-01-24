import shutil

from .supports.image_message.image_message import ImageMessage
from .supports.text_message import TextMessage


class Thread:
    COLORS = {
        "border": "\033[38;5;75m",
        "header": "\033[1;36m",
        "role": "\033[1;33m",
        "content": "\033[0;37m",
        "reset": "\033[0m",
    }

    def __init__(self):
        self.messages = []

    @classmethod
    def add_first_message(cls, role="user", text="", **kwargs):
        return cls().add_message(role, text, **kwargs)

    @classmethod
    def from_dicts(cls, messages: list[dict]) -> "Thread":
        t = cls()
        for m in messages:
            t.add_message(m.get("role", "user"), m.get("content", ""))
        return t

    def add_message(self, role, text="", **kwargs):
        image_data = kwargs.get("image_data")
        message_class = ImageMessage if image_data is not None else TextMessage
        message_kwargs = {"image_data": image_data} if image_data is not None else {}
        self.messages.append(message_class(role=role, text=text, **message_kwargs))
        return self

    def get_printable_representation(self):
        terminal_width = shutil.get_terminal_size().columns
        colors = self.COLORS
        reset_color = colors["reset"]
        border_color = colors["border"]
        color_values = tuple(colors.values())

        border = lambda chars: f"{border_color}{chars[0]}{'═' * (terminal_width - 2)}{chars[1]}{reset_color}"
        pad = lambda content: " " * (
            terminal_width - 4 - len(content) + sum(content.count(value) * len(value) for value in color_values)
        )
        line = lambda content: f"{border_color}│{reset_color} {content}{pad(content)} {border_color}│{reset_color}"

        middle_border = border("├┤")
        output = [border("╭╮"), line(f"{colors['header']}Messages:{reset_color}"), middle_border]

        for index, message in enumerate(self.messages, 1):
            output.append(
                line(
                    f"{colors['header']}Message {index} | Role: {colors['role']}{str(message.role).capitalize()}{reset_color}"
                )
            )
            output.append(middle_border)
            output.extend(line(content) for content in message.get_str_representation(colors, terminal_width))
            output.append(middle_border)

        output[-1] = border("╰╯")
        return "\n".join(output)

    def get_messages_as_dicts(self):
        return [message.to_dict() for message in self.messages]

    def get_concatenated_content(self, include_roles: bool = True, separator: str = "\n\n") -> str:
        return separator.join(
            (f"{message['role']}: " if include_roles and message.get("role") else "") + message["content"]
            for message in self.get_messages_as_dicts()
            if message.get("content")
        )
