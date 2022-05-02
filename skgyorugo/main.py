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
import scripts.alwase
import scripts.chatting
import database_manager
import analyze_auto_message
import time
import logging
from importlib import reload

reload(tools.raid)
reload(tools.smart_privmsg)
reload(tools.permissions)
reload(analyze_command)
reload(scripts.unit_converter)
reload(scripts.alwase)
reload(scripts.chatting)
reload(database_manager)
reload(analyze_auto_message)

logging.basicConfig(
    filename="/var/log/aptbot/logs.log",
    level=logging.DEBUG,
    format="[%(levelname)s] %(asctime)s: %(message)s"
)

PATH = os.path.dirname(os.path.realpath(__file__))
logging.info(f"Defined PATH: {PATH}")
COMMANDS_PATH = os.path.join(PATH, "commands")
logging.info(f"Defined COMMANDS_PATH: {COMMANDS_PATH}")
AUTO_MESSAGES_PATH = os.path.join(PATH, "auto_messages")
logging.info(f"Defined AUTO_MESSAGES_PATH: {AUTO_MESSAGES_PATH}")

commands_specs = {}
commands_modules = {}

auto_message_specs = {}
auto_message_modules = {}

commands = [
    c for c in os.listdir(COMMANDS_PATH) if os.path.isfile(os.path.join(COMMANDS_PATH, c))
]
commands = filter(lambda x: not x.startswith('.'), commands)
commands = filter(lambda x: os.path.splitext(x)[1] == ".py", commands)
commands = list(commands)
for command in commands:
    commands_specs[command.split('.')[0]] = (
        importlib.util.spec_from_file_location(
            f"{command.split('.')[0]}",
            os.path.join(COMMANDS_PATH, command)
        )
    )
logging.info(f"List of commands: {commands}")

auto_messages = [
    c for c in os.listdir(AUTO_MESSAGES_PATH) if os.path.isfile(os.path.join(AUTO_MESSAGES_PATH, c))
]
auto_messages = filter(lambda x: not x.startswith('.'), auto_messages)
auto_messages = filter(
    lambda x: os.path.splitext(x)[1] == ".py",
    auto_messages
)
auto_messages = list(auto_messages)
for auto_message in auto_messages:
    auto_message_specs[auto_message.split('.')[0]] = (
        importlib.util.spec_from_file_location(
            f"{auto_message.split('.')[0]}",
            os.path.join(AUTO_MESSAGES_PATH, auto_message)
        )
    )
logging.info(f"List of auto_messages: {auto_messages}")

for spec in commands_specs:
    commands_modules[spec] = importlib.util.module_from_spec(
        commands_specs[spec])
    if not commands_specs[spec]:
        continue
    try:
        commands_specs[spec].loader.exec_module(commands_modules[spec])
    except Exception as e:
        logging.critical(traceback.format_exc())
        logging.critical(f"Problem Loading Module: {e}")

for spec in auto_message_specs:
    auto_message_modules[spec] = importlib.util.module_from_spec(
        auto_message_specs[spec])
    if not auto_message_specs[spec]:
        continue
    try:
        auto_message_specs[spec].loader.exec_module(auto_message_modules[spec])
    except Exception as e:
        logging.critical(traceback.format_exc())
        logging.critical(f"Problem Loading Module: {e}")


database_manager.create_database()
database_manager.create_variables_db()
database_manager.create_chat_history_database()
database_manager.update_commands_in_database(commands_modules, commands)
database_manager.update_auto_messages_in_database(
    auto_message_modules, auto_messages)


def start(bot: Bot, message: Message):
    while True:
        analyze_auto_message.do_auto_message(bot, message, auto_message_modules)
        time.sleep(30)


def main(bot: Bot, message: Message):
    if message.command == Commands.PRIVMSG:
        database_manager.add_message_to_chat_history(message)
        analyze_command.do_command(bot, message, commands_modules)
        scripts.unit_converter.send_metric(bot, message)
        scripts.alwase.alwase(bot, message)
        scripts.chatting.chatting(bot, message)
        scripts.chatting.chatting_annoy(bot, message)

    tools.raid.raid(bot, message)
