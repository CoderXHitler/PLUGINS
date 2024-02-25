import os
import time

import requests
from pyrogram.types import Message

from Arankbot.core import ENV
from Arankbot.functions.formatter import readable_time
from Arankbot.functions.images import get_wallpapers, make_logo

from . import Config, HelpMenu, db, Arankbot, on_message


@on_message("logo", allow_stan=True)
async def makeLogo(_, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(message, "Provide a text to make a logo.")

    start_time = time.time()
    Arank = await Arankbot.edit(message, "Processing...")
    query = await Arankbot.input(message)

    if message.reply_to_message and message.reply_to_message.photo:
        photo = await message.reply_to_message.download(Config.TEMP_DIR + "temp_bg.jpg")
        text = query
    else:
        if "--" in query:
            text, theme = query.split("--", 1)
            isRandom = False
        else:
            text, theme = query, ""
            isRandom = True

        access = await db.get_env(ENV.unsplash_api)
        if not access:
            return await Arankbot.delete(
                Arank, "Unsplash API not found. Either set it or reply to an image."
            )

        photo = await get_wallpapers(access, 1, theme.strip(), isRandom)
        if not photo:
            return await Arankbot.delete(Arank, "No wallpapers found.")

        binary = requests.get(photo[0]).content
        with open(Config.TEMP_DIR + "temp_bg.jpg", "wb") as f:
            f.write(binary)

    logo_path = await make_logo(Config.TEMP_DIR + "temp_bg.jpg", text.strip(), Config.FONT_PATH)
    time_taken = readable_time(int(time.time() - start_time))

    await message.reply_photo(
        logo_path,
        caption=f"**𝖫𝗈𝗀𝗈 𝖬𝖺𝖽𝖾 𝗂𝗇:** `{time_taken}`",
    )
    await Arank.delete()
    os.remove(logo_path)


@on_message("setfont", allow_stan=True)
async def setFont(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await Arankbot.delete(message, "Reply to a font file to save it.")

    Arank = await Arankbot.edit(message, "Processing...")
    font = await message.reply_to_message.download(Config.DWL_DIR)

    if not font.endswith(".ttf"):
        return await Arankbot.delete(Arank, "Invalid font file. Only .ttf is supported.")

    if not os.path.exists(font):
        return await Arankbot.delete(Arank, "Font not found.")

    Config.FONT_PATH = font
    await Arankbot.delete(Arank, "Font set successfully.")


@on_message("resetfont", allow_stan=True)
async def resetFont(_, message: Message):
    prev_font = Config.FONT_PATH
    if prev_font == "./Arankbot/resources/fonts/Montserrat.ttf":
        return await Arankbot.delete(message, "Font is already set to default.")

    Config.FONT_PATH = "./Arankbot/resources/fonts/Montserrat.ttf"
    await Arankbot.delete(message, "Font reset successfully.")
    os.remove(prev_font)


HelpMenu("logo").add(
    "logo",
    "<reply to image (optional)> <text>",
    "Make a logo with text. You can also reply to an image to use it as a background. You can also specify a theme by using `--` after the text.",
    "logo The ArankBot --supra",
    "This command uses Unsplash API to get images.",
).add(
    "setfont",
    "<reply to font file>",
    "Set a font file to use for logo making. This is not permanent option.",
    "setfont",
    "Only .ttf files are supported.",
).add(
    "resetfont",
    None,
    "Reset the font file to default.",
    "resetfont",
).info(
    "Make Logos"
).done()
