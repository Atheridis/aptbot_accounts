from aptbot.bot import Bot, Message, Commands
import os
import importlib
import importlib.util
import traceback
import tools.raid
import tools.smart_privmsg
import tools.permissions
import analyze_command
import scripts.unit_converter
import database_manager
from importlib import reload

reload(tools.raid)
reload(tools.smart_privmsg)
reload(tools.permissions)
reload(analyze_command)
reload(scripts.unit_converter)
reload(database_manager)


PATH = os.path.dirname(os.path.realpath(__file__))
COMMANDS_PATH = os.path.join(PATH, "commands")
AUTO_MESSAGES_PATH = os.path.join(PATH, "auto_messages")

specs = {}
modules = {}

commands = [
    c for c in os.listdir(COMMANDS_PATH) if os.path.isfile(os.path.join(COMMANDS_PATH, c))
]
commands = filter(lambda x: not x.startswith('.'), commands)
commands = filter(lambda x: os.path.splitext(x)[1] == ".py", commands)
commands = list(commands)
for command in commands:
    specs[command.split('.')[0]] = (
        importlib.util.spec_from_file_location(
            f"{command.split('.')[0]}",
            os.path.join(COMMANDS_PATH, command)
        )
    )

auto_messages = [
    c for c in os.listdir(COMMANDS_PATH) if os.path.isfile(os.path.join(COMMANDS_PATH, c))
]
auto_messages = filter(lambda x: not x.startswith('.'), auto_messages)
auto_messages = filter(
    lambda x: os.path.splitext(x)[1] == ".py",
    auto_messages
)
auto_messages = list(auto_messages)
for auto_message in auto_messages:
    specs[auto_message.split('.')[0]] = (
        importlib.util.spec_from_file_location(
            f"{auto_message.split('.')[0]}",
            os.path.join(COMMANDS_PATH, auto_message)
        )
    )

for spec in specs:
    modules[spec] = importlib.util.module_from_spec(specs[spec])
    if not specs[spec]:
        continue
    try:
        specs[spec].loader.exec_module(modules[spec])
    except Exception as e:
        print()
        print(traceback.format_exc())
        print(f"Problem Loading Module: {e}")


database_manager.create_database()
database_manager.update_commands_in_database(modules, commands)


def main(bot: Bot, message: Message):
    if message.command == Commands.PRIVMSG:
        analyze_command.do_command(bot, message, modules)
        scripts.unit_converter.send_metric(bot, message)

    tools.raid.raid(bot, message)
