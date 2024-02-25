import time

from pyrogram.types import Message
from pySmartDL import SmartDL

from Arankbot.core import LOGS, Symbols
from Arankbot.functions.formatter import readable_time
from Arankbot.functions.tools import progress

from . import Config, HelpMenu, Arankbot, on_message


@on_message("download", allow_stan=True)
async def download(_, message: Message):
    Arank = await Arankbot.edit(message, "Starting to download...")
    if message.reply_to_message and message.reply_to_message.media:
        start_time = time.time()
        try:
            dwl_path = await message.reply_to_message.download(
                Config.DWL_DIR,
                progress=progress,
                progress_args=(
                    Arank,
                    start_time,
                    "⬇️ Downloading",
                ),
            )
        except Exception as e:
            return await Arankbot.error(Arank, f"`{e}`", 10)

        await Arank.edit(
            f"**Downloaded to** `{dwl_path}` **in** {readable_time(round(time.time() - start_time))} seconds.**"
        )

    elif len(message.command) > 2:
        dwl_url = (await Arankbot.input(message)).split(" ")
        start_time = time.time()
        try:
            dl = SmartDL(dwl_url, Config.DWL_DIR, progress_bar=False)
            dl.start(blocking=False)
            while not dl.isFinished():
                display_msg = ""
                downloaded_size = dl.get_dl_size(human=True)
                file_size = dl.filesize or "Unknown"
                diff = time.time() - start_time
                speed = dl.get_speed(human=True)
                dl_percentage = round((dl.get_progress() * 100), 2)
                eta = dl.get_eta(human=True)
                try:
                    current_msg = (
                        f"**⬇️ Downloading...**\n\n"
                        f"**{Symbols.anchor} URL:** `{dwl_url}`\n"
                        f"**{Symbols.anchor} Downloaded:** `{downloaded_size}` of `{file_size}`\n"
                        f"**{Symbols.anchor} Speed:** `{speed}`\n"
                        f"**{Symbols.anchor} ETA:** `{eta}`\n"
                        f"**{Symbols.anchor} Progress:** `{dl_percentage}%`"
                    )
                    if round(diff % 10.00) == 0 and current_msg != display_msg:
                        await Arank.edit(current_msg)
                        display_msg = current_msg
                except Exception as e:
                    LOGS.warning(f"PySmartDl: {str(e)}")

            end_time = readable_time(round(time.time() - start_time))
            if dl.isSuccessful():
                await Arank.edit(
                    f"**Downloaded to** `{dl.get_dest()}` **in** `{end_time}` **seconds.**"
                )
            else:
                await Arankbot.error(Arank, f"**Failed to download** `{len(dwl_url)} url(s)`")
        except Exception as e:
            return await Arankbot.error(Arank, f"`{e}`", 10)
    else:
        return await Arankbot.delete(
            message, "Reply to a media message or pass direct urls to download it."
        )


HelpMenu("downloads").add(
    "download",
    "<reply to media> or <direct link>",
    "Download media to server.",
    "download https://example.com/file.mp4",
    "You can pass multiple urls to download it on my server.",
).info("Downloader").done()
