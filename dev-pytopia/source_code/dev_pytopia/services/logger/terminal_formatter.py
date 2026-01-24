from datetime import datetime
import logging
from os.path import abspath
from shutil import get_terminal_size

from colorama import Back, Fore, Style


class TerminalFormatter(logging.Formatter):
    LOG_LEVEL_STYLES = {
        "TRACE": (Style.DIM + Fore.WHITE, "🔬"),
        "INSPECT": (Style.DIM + Fore.GREEN, "🛠️"),
        "SEARCH": (Style.NORMAL + Fore.BLUE, "🔍"),
        "OBSERVE": (Style.BRIGHT + Fore.CYAN, "👀"),
        "INFO": (Style.NORMAL + Fore.WHITE, "ℹ️"),
        "CONCERN": (Style.DIM + Fore.YELLOW, "🤔"),
        "SUSPECT": (Style.BRIGHT + Back.LIGHTMAGENTA_EX + Fore.WHITE, "🐛"),
        "ERROR": (Style.BRIGHT + Back.LIGHTMAGENTA_EX + Fore.WHITE, "🚨"),
        "DANGER": (Style.BRIGHT + Back.LIGHTRED_EX + Fore.WHITE, "⛔️"),
        "SHOWSTOPPER": (Style.DIM + Back.BLACK + Fore.RED, "💀"),
    }

    def format(self, record):
        metadata, message = record.msg.split("\nCONTENT:\n", 1)
        style, emoji = self.LOG_LEVEL_STYLES.get(record.levelname, self.LOG_LEVEL_STYLES["INFO"])
        width, R = get_terminal_size().columns, Style.RESET_ALL

        ts = datetime.fromtimestamp(record.created)
        time_str = f"{ts.strftime('%I:%M %p')} ({ts.second}s {ts.microsecond // 1000}ms {ts.microsecond % 1000}μs)"

        location_lines = "\n".join(
            f"{line[: len(line) - len(line.lstrip())]}{style}🔹 Path: \u001b[48;5;54m\u001b[4m{abspath(line.split(':', 1)[1].strip())}\u001b[24m{R}"
            if "🔹 Path:" in line
            else f"{line[: len(line) - len(line.lstrip())]}{style}{line.strip()}{R}"
            for line in metadata.splitlines()
            if line.strip()
        )

        yellow_bar = f"{Style.BRIGHT}{Back.YELLOW}{Fore.BLACK}"
        return (
            f"\n{Style.BRIGHT}{Back.WHITE}{Fore.BLACK}{'═' * width}{R}\u001b[K\n"
            f"\n{style}{emoji}  {record.levelname} LOG{R}\n    {style}⏰ Time: {time_str}{R}\n{location_lines}\n\n"
            f"{yellow_bar}{'=== CONTENT ==='.center(width)}{R}\n\n"
            f"{Style.NORMAL}{Fore.WHITE}{message.strip()}{R}\n\n"
            f"{yellow_bar}{'═' * width}{R}\u001b[K"
        )
