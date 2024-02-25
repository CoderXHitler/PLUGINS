from pyrogram.enums import ChatType

from Arankbot.core.clients import Arankbot
from Arankbot.core.config import Config, Symbols
from Arankbot.core.database import db
from Arankbot.plugins.decorator import custom_handler, on_message
from Arankbot.plugins.help import HelpMenu

handler = Config.HANDLERS[0]
bot = Arankbot.bot

bot_only = [ChatType.BOT]
group_n_channel = [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]
group_only = [ChatType.GROUP, ChatType.SUPERGROUP]
private_n_bot = [ChatType.PRIVATE, ChatType.BOT]
private_only = [ChatType.PRIVATE]
