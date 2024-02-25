from pyrogram import idle

from Arankbot import __version__
from Arankbot.core import Config, ForcesubSetup, UserSetup, db, Arankbot
from Arankbot.functions.tools import initialize_git
from Arankbot.functions.utility import BList, Flood, TGraph


async def main():
    await Arankbot.startup()
    await db.connect()
    await UserSetup()
    await ForcesubSetup()
    await Flood.updateFromDB()
    await BList.updateBlacklists()
    await TGraph.setup()
    await initialize_git(Config.PLUGINS_REPO)
    await Arankbot.start_message(__version__)
    await idle()


if __name__ == "__main__":
    Arankbot.run(main())
