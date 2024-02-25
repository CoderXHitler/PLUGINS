import os
import time

import requests
from PIL import Image
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message

from Arankbot.core import ENV
from Arankbot.functions.convert import tgs_to_png, video_to_png
from Arankbot.functions.formatter import readable_time
from Arankbot.functions.images import create_thumbnail, draw_meme
from Arankbot.functions.media import get_metedata
from Arankbot.functions.paste import post_to_telegraph
from Arankbot.functions.tools import progress, runcmd
from Arankbot.functions.utility import TGraph

from . import Config, HelpMenu, db, Arankbot, on_message


@on_message("mediainfo", allow_stan=True)
async def mediaInfo(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await Arankbot.delete(message, "Reply to a media file")

    media = message.reply_to_message.media
    Arank = await Arankbot.edit(message, "Getting media info...")

    if media == MessageMediaType.ANIMATION:
        media_file = message.reply_to_message.animation
    elif media == MessageMediaType.AUDIO:
        media_file = message.reply_to_message.audio
    elif media == MessageMediaType.DOCUMENT:
        media_file = message.reply_to_message.document
    elif media == MessageMediaType.PHOTO:
        media_file = message.reply_to_message.photo
    elif media == MessageMediaType.STICKER:
        media_file = message.reply_to_message.sticker
    elif media == MessageMediaType.VIDEO:
        media_file = message.reply_to_message.video
    else:
        return await Arankbot.delete(message, "Unsupported media type")

    metadata = await get_metedata(media_file)
    if not metadata:
        return await Arankbot.delete(message, "Failed to get media info")

    await Arank.edit(f"Fetched metadata, now fetching extra mediainfo...")

    start_time = time.time()
    try:
        file_path = await message.reply_to_message.download(
            Config.DWL_DIR,
            progress=progress,
            progress_args=(Arank, start_time, "⬇️ Downloading"),
        )
    except Exception:
        return await Arank.edit(
            f"**Failed to download media check the metadata instead!**\n\n{metadata}"
        )

    out, _, _, _ = await runcmd(f"mediainfo '{file_path}'")
    if not out:
        return await Arank.edit(
            f"Failed to get mediainfo, check the metadata instead!\n\n{metadata}"
        )

    await Arank.edit(f"Uploading mediainfo to telegraph...")

    to_paste = f"<h1>💫 ArankBot Media Info:</h1><br>{metadata}<br><b>📝 MediaInfo:</b><br><code>{out}</code>"
    link = post_to_telegraph("ArankBotMediaInfo", to_paste)

    await Arank.edit(f"**📌 Media Info:** [Here]({link})", disable_web_page_preview=True)
    os.remove(file_path)


@on_message(["mmf", "memify"], allow_stan=True)
async def memify(_, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(message, "Enter some text!")

    if not message.reply_to_message or not message.reply_to_message.media:
        return await Arankbot.delete(message, "Reply to a media file")

    start_time = time.time()
    Arank = await Arankbot.edit(message, "Memifying...")
    file = await message.reply_to_message.download(
        Config.DWL_DIR,
        progress=progress,
        progress_args=(Arank, start_time, "⬇️ Downloading"),
    )

    text = await Arankbot.input(message)
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text, lower_text = text, ""

    if file and file.endswith(".tgs"):
        await Arank.edit("Looks like an animated sticker, converting to image...")
        pic = await tgs_to_png(file)
    elif file and file.endswith((".webp", ".png")):
        pic = Image.open(file).save(file, "PNG", optimize=True)
    elif file:
        await Arank.edit("Converting to image...")
        pic, status = await video_to_png(file, 0)
        if status == False:
            return await Arankbot.error(Arank, pic)
    else:
        return await Arankbot.delete(message, "Unsupported media type")

    await Arank.edit("Adding text...")
    memes = await draw_meme(file, upper_text, lower_text)

    await Arankbot.delete(Arank, "Done!")
    await message.reply_sticker(memes[1])
    await message.reply_photo(
        memes[0],
        caption=f"**🍀 𝖬𝖾𝗆𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝗂𝗇𝗀 𝖧𝖾𝗅𝗅𝖡𝗈𝗍!**",
    )

    os.remove(pic)
    os.remove(file)
    os.remove(memes[0])
    os.remove(memes[1])


@on_message("setthumbnail", allow_stan=True)
async def set_thumbnail(_, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(
            message, "Reply to a media file to set as thumbnail!"
        )

    if not message.reply_to_message or not message.reply_to_message.media:
        return await Arankbot.delete(
            message, "Reply to a media file to set as thumbnail!"
        )

    media = message.reply_to_message.media
    if media not in MessageMediaType.PHOTO:
        return await Arankbot.delete(
            message,
            "Only photos are supported! If this is a file, try converting it to a photo first.",
        )

    if message.reply_to_message.photo.file_size >= 5242880:
        return await Arankbot.delete(
            message,
            "This photo is too big to upload to telegraph! You need to choose a photo below 5mb.",
        )

    Arank = await Arankbot.edit(message, "Uploading to telegraph...")
    path = await message.reply_to_message.download(Config.TEMP_DIR)

    try:
        media_url = TGraph.telegraph.upload_file(path)
        url = f"https://te.legra.ph{media_url[0]['src']}"
    except Exception as e:
        return await Arankbot.error(Arank, str(e))

    await db.set_env(ENV.thumbnail_url)
    await Arankbot.delete(Arank, f"Thumbnail set to [this image]({url})!", 20)
    os.remove(path)


@on_message("rename", allow_stan=True)
async def renameMedia(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await Arankbot.delete(message, "Reply to a media file to rename it!")

    media = message.reply_to_message.media
    if media not in [
        MessageMediaType.AUDIO,
        MessageMediaType.DOCUMENT,
        MessageMediaType.PHOTO,
        MessageMediaType.VIDEO,
        MessageMediaType.VOICE,
        MessageMediaType.ANIMATION,
        MessageMediaType.STICKER,
        MessageMediaType.VIDEO_NOTE,
    ]:
        return await Arankbot.delete(message, "Unsupported media type!")

    if len(message.command) < 2:
        return await Arankbot.delete(
            message, "You need to provide a new filename with extention!"
        )

    new_name = await Arankbot.input(message)
    Arank = await Arankbot.edit(message, f"Renaming to `{new_name}` ...")

    strart_time = time.time()
    renamed_file = await message.reply_to_message.download(
        Config.DWL_DIR + new_name,
        progress=progress,
        progress_args=(Arank, strart_time, "⬇️ Downloading"),
    )

    dwl_time = readable_time(int(strart_time - time.time()))
    await Arank.edit(f"**Downloaded and Renamed in** `{dwl_time}`**,** __uploading...__")

    start2 = time.time()

    thumb = await db.get_env(ENV.thumbnail_url)
    if thumb:
        binary = requests.get(thumb).content
        photo = f"{Config.TEMP_DIR}/thumb_{int(time.time())}.jpeg"
        with open(photo, "wb") as f:
            f.write(binary)
        thumbnail = create_thumbnail(photo, (320, 320), 199)
    else:
        photo = None
        thumbnail = None

    await message.reply_document(
        renamed_file,
        thumb=thumbnail,
        caption=f"**📁 File Name:** `{new_name}`",
        file_name=new_name,
        force_document=True,
        progress=progress,
        progress_args=(Arank, start2, "⬆️ Uploading"),
    )

    end_time = readable_time(int(start2 - time.time()))
    total_time = readable_time(int(strart_time - time.time()))
    await Arank.edit(
        f"**📁 File Name:** `{new_name}`\n\n**⬇️ Downloaded in:** `{dwl_time}`\n**⬆️ Uploaded in:** `{end_time}`\n**💫 Total time taken:** `{total_time}`"
    )
    os.remove(renamed_file)
    if photo:
        os.remove(photo)


HelpMenu("media").add(
    "mediainfo",
    "<reply to media message>",
    "Get the metadata and detailed media info of replied media file.",
    "mediainfo",
).add(
    "memify",
    "<reply to media message> <upper text>;<lower text>",
    "Add text to a media file and make it a meme.",
    "memify Aranko World",
    "When ';' is used, the text before it will be the upper text and the text after it will be the lower text.",
).add(
    "rename",
    "<reply to media message> <new file name>",
    "Rename a media file with the provided name.",
    "rename ArankBot.jpg",
    "The file name must have an extention.",
).add(
    "setthumbnail",
    "<reply to photo>",
    "Set the replied photo as the thumbnail of the bot for all the upload/rename function.",
    "setthumbnail <reply>",
    "The photo must be below 5mb and in photo format and not in file.",
).info(
    "Media utils"
).done()
