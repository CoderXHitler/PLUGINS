import os
import time

import requests
from lyricsgenius import Genius
from pyrogram import Client
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message
from yt_dlp import YoutubeDL

from Arankbot.core import ENV
from Arankbot.functions.driver import YoutubeDriver
from Arankbot.functions.paste import post_to_telegraph
from Arankbot.functions.tools import progress

from . import HelpMenu, Symbols, db, Arankbot, on_message


@on_message("song", allow_stan=True)
async def dwlSong(_, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(message, "Provide a song name to download.")

    query = await Arankbot.input(message)
    Arank = await Arankbot.edit(message, f"🔎 __𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀 𝖲𝗈𝗇𝗀__ `{query}`...")

    ytSearch = YoutubeDriver(query, 1).to_dict()[0]
    upload_text = f"**⬆️ 𝖴𝗉𝗅𝗈𝖺𝖽𝗂𝗇𝗀 𝖲𝗈𝗇𝗀 ...** \n\n**{Symbols.anchor} 𝖳𝗂𝗍𝗅𝖾:** `{ytSearch['title'][:50]}`\n**{Symbols.anchor} 𝖢𝗁𝖺𝗇𝗇𝖾𝗅:** `{ytSearch['channel']}`"

    try:
        url = f"https://www.youtube.com{ytSearch['url_suffix']}"
        with YoutubeDL(YoutubeDriver.song_options()) as ytdl:
            yt_data = ytdl.extract_info(url, False)
            yt_file = ytdl.prepare_filename(yt_data)
            ytdl.process_info(yt_data)

        await Arank.edit(upload_text)
        resp = requests.get(ytSearch["thumbnail"])
        with open(f"{yt_file}.jpg", "wb") as thumbnail:
            thumbnail.write(resp.content)

        start_time = time.time()
        await message.reply_audio(
            f"{yt_file}.mp3",
            caption=f"**🎧 𝖳𝗂𝗍𝗅𝖾:** {ytSearch['title']} \n\n**👀 𝖵𝗂𝖾𝗐𝗌:** `{ytSearch['views']}` \n**⌛ 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇:** `{ytSearch['duration']}`",
            duration=int(yt_data["duration"]),
            performer="[тнє нєℓℓвσт]",
            title=ytSearch["title"],
            thumb=f"{yt_file}.jpg",
            progress=progress,
            progress_args=(
                Arank,
                start_time,
                upload_text,
            ),
        )
        await Arank.delete()
    except Exception as e:
        return await Arankbot.delete(Arank, f"**🍀 𝖲𝗈𝗇𝗀 𝖭𝗈𝗍 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝖽:** `{e}`")

    try:
        os.remove(f"{yt_file}.mp3")
        os.remove(f"{yt_file}.jpg")
    except:
        pass


@on_message("video", allow_stan=True)
async def dwlSong(_, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(message, "Provide a song name to download.")

    query = await Arankbot.input(message)
    Arank = await Arankbot.edit(message, f"🔎 __𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀 𝖵𝗂𝖽𝖾𝗈 𝖲𝗈𝗇𝗀__ `{query}`...")

    ytSearch = YoutubeDriver(query, 1).to_dict()[0]
    upload_text = f"**⬆️ 𝖴𝗉𝗅𝗈𝖺𝖽𝗂𝗇𝗀 𝖵𝗂𝖽𝖾𝗈 𝖲𝗈𝗇𝗀 ...** \n\n**{Symbols.anchor} 𝖳𝗂𝗍𝗅𝖾:** `{ytSearch['title'][:50]}`\n**{Symbols.anchor} 𝖢𝗁𝖺𝗇𝗇𝖾𝗅:** `{ytSearch['channel']}`"

    try:
        url = f"https://www.youtube.com{ytSearch['url_suffix']}"
        with YoutubeDL(YoutubeDriver.video_options()) as ytdl:
            yt_data = ytdl.extract_info(url, True)
            yt_file = yt_data["id"]

        await Arank.edit(upload_text)
        resp = requests.get(ytSearch["thumbnail"])
        with open(f"{yt_file}.jpg", "wb") as thumbnail:
            thumbnail.write(resp.content)

        start_time = time.time()
        await message.reply_video(
            f"{yt_file}.mp4",
            caption=f"**🎧 𝖳𝗂𝗍𝗅𝖾:** {ytSearch['title']} \n\n**👀 𝖵𝗂𝖾𝗐𝗌:** `{ytSearch['views']}` \n**⌛ 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇:** `{ytSearch['duration']}`",
            duration=int(yt_data["duration"]),
            thumb=f"{yt_file}.jpg",
            progress=progress,
            progress_args=(
                Arank,
                start_time,
                upload_text,
            ),
        )
        await Arank.delete()
    except Exception as e:
        return await Arankbot.delete(Arank, f"**🍀 𝖵𝗂𝖽𝖾𝗈 𝖲𝗈𝗇𝗀 𝖭𝗈𝗍 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝖽:** `{e}`")

    try:
        os.remove(f"{yt_file}.mp4")
        os.remove(f"{yt_file}.jpg")
    except:
        pass


@on_message("lyrics", allow_stan=True)
async def getlyrics(_, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(message, "Provide a song name to fetch lyrics.")

    api = await db.get_env(ENV.lyrics_api)
    if not api:
        return await Arankbot.delete(message, "Lyrics API not found.")

    query = await Arankbot.input(message)
    if "-" in query:
        artist, song = query.split("-")
    else:
        artist, song = "", query

    Arank = await Arankbot.edit(message, f"🔎 __𝖫𝗒𝗋𝗂𝖼𝗌 𝖲𝗈𝗇𝗀__ `{query}`...")

    genius = Genius(
        api,
        verbose=False,
        remove_section_headers=True,
        skip_non_songs=True,
        excluded_terms=["(Remix)", "(Live)"],
    )

    song = genius.search_song(song, artist)
    if not song:
        return await Arankbot.delete(Arank, "No results found.")

    title = song.full_title
    image = song.song_art_image_url
    artist = song.artist
    lyrics = song.lyrics

    outStr = f"<b>{Symbols.anchor} Title:</b> <code>{title}</code>\n<b>{Symbols.anchor} Artist:</b> <code>{artist}</code>\n\n<code>{lyrics}</code>"
    try:
        await Arank.edit(outStr, disable_web_page_preview=True)
    except MessageTooLong:
        content = f"<img src='{image}'/>\n\n{outStr}"
        url = post_to_telegraph(title, content)
        await Arank.edit(
            f"**{Symbols.anchor} Title:** `{title}`\n**{Symbols.anchor} Artist:** `{artist}`\n\n**{Symbols.anchor} Lyrics:** [Click Here]({url})",
            disable_web_page_preview=True,
        )


HelpMenu("songs").add(
    "song",
    "<song name>",
    "Download the given audio song from Youtube!",
    "song believer",
).add(
    "video",
    "<song name>",
    "Download the given video song from Youtube!",
    "song believer",
).add(
    "lyrics",
    "<song name>",
    "Get the lyrics of the given song! Give artist name after - to get accurate results.",
    "lyrics believer - imagine dragons",
    "Need to setup Lyrics Api key from https://genius.com/developers",
).info(
    "Song and Lyrics"
).done()
