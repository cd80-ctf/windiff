import datetime

from rich.text import Text
from rich.console import Console
g_console = Console()


def get_datetime_header():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f") + " | "


def error(message):
    g_console.print(Text.assemble(get_datetime_header(), ("[ERROR] ", "bold red"), message))


def warning(message):
    g_console.print(Text.assemble(get_datetime_header(), ("[WARNING] ", "bold orange"), message))


def info(message):
    g_console.print(Text.assemble(get_datetime_header(), ("[INFO] ", "bold white"), message))
