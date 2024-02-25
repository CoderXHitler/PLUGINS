import io
import re
import subprocess
import sys
import traceback

import bs4
import requests
from pyrogram import Client
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message
from speedtest import Speedtest

from . import HelpMenu, Arankbot, on_message


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@on_message("eval", allow_stan=True)
async def runeval(client: Client, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(message, "No python code provided!")

    reply_to = message.reply_to_message or message

    code = await Arankbot.input(message)
    Arank = await Arankbot.edit(message, "`running...`")

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(code, client, message)
    except Exception:
        exc = traceback.format_exc()

    evaluation = ""
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    heading = f"**𝖤𝗏𝖺𝗅:**\n```python\n{code}```\n\n"
    output = f"**𝖮𝗎𝗍𝗉𝗎𝗍:**\n`{evaluation.strip()}`"
    final_output = heading + output

    try:
        await reply_to.reply_text(final_output, disable_web_page_preview=True)
    except MessageTooLong:
        with io.BytesIO(str.encode(output)) as out_file:
            out_file.name = "eval.txt"
            await reply_to.reply_document(out_file, caption=heading)

    await Arank.delete()


@on_message(["exec", "term"], allow_stan=True)
async def runterm(client: Client, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(message, "No sArank code provided!")

    reply_to = message.reply_to_message or message

    cmd = await Arankbot.input(message)
    Arank = await Arankbot.edit(message, "`running...`")

    if "\n" in cmd:
        code = cmd.split("\n")
        output = ""
        for x in code:
            sArank = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            try:
                process = subprocess.Popen(
                    sArank, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            except Exception as err:
                print(err)
                await Arank.edit(f"**Error:** \n`{err}`")
            output += f"**{code}**\n"
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        sArank = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", cmd)
        for a in range(len(sArank)):
            sArank[a] = sArank[a].replace('"', "")
        try:
            process = subprocess.Popen(
                sArank, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(exc_type, exc_obj, exc_tb)
            await Arank.edit("**Error:**\n`{}`".format("".join(errors)))
            return
        output = process.stdout.read()[:-1].decode("utf-8")

    if str(output) == "\n":
        return await Arank.edit(f"**𝖮𝗎𝗍𝗉𝗎𝗍:** __𝖭𝗈 𝗈𝗎𝗍𝗉𝗎𝗍!__")
    else:
        try:
            await reply_to.reply_text(
                f"**{client.me.id}@Arankbot:~$** `{cmd}`\n\n**𝖮𝗎𝗍𝗉𝗎𝗍:**\n```\n{output}```"
            )
        except MessageTooLong:
            with io.BytesIO(str.encode(output)) as out_file:
                out_file.name = "exec.txt"
                await reply_to.reply_document(
                    out_file,
                    caption=f"**{client.me.id}@Arankbot:~$** `{cmd}`",
                )

    await Arank.delete()


@on_message(["sh", "sArank"], allow_stan=True)
async def runsArank(_, message: Message):
    if len(message.command) < 2:
        return await Arankbot.delete(message, "No sArank code provided!")

    code = await Arankbot.input(message)
    Arank = await Arankbot.edit(message, "`executing...`")

    result = subprocess.run(code, sArank=True, capture_output=True, text=True)
    output = result.stdout + result.stderr

    heading = f"**𝖲𝗁𝖾𝗅𝗅:**\n```sh\n{code}```\n\n"
    output = f"**𝖮𝗎𝗍𝗉𝗎𝗍:**\n`{output.strip()}`"
    final_output = heading + output

    try:
        await message.reply_text(final_output, disable_web_page_preview=True)
    except MessageTooLong:
        with io.BytesIO(str.encode(output)) as out_file:
            out_file.name = "sArank.txt"
            await message.reply_document(out_file, caption=heading)

    await Arank.delete()


@on_message("fext", allow_stan=True)
async def file_extention(_, message: Message):
    BASE_URL = "https://www.fileext.com/file-extension/{0}.html"
    if len(message.command) < 2:
        return await Arankbot.delete(message, "No file extention provided!")

    extention = message.command[1]
    Arank = await Arankbot.edit(message, "`getting information...`")

    response = requests.get(BASE_URL.format(extention))
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.content, "html.parser")
        details = soup.find_all("td", {"colspan": "3"})[-1].text
        await Arank.edit(f"**𝖥𝗂𝗅𝖾 𝖤𝗑𝗍𝖾𝗇𝗍𝗂𝗈𝗇:** `{extention}`\n\n**𝖣𝖾𝗍𝖺𝗂𝗅𝗌:**\n`{details}`")
    else:
        await Arank.edit(f"**𝖥𝗂𝗅𝖾 𝖤𝗑𝗍𝖾𝗇𝗍𝗂𝗈𝗇:** `{extention}`\n\n**𝖣𝖾𝗍𝖺𝗂𝗅𝗌:**\n`Not Found`")


@on_message("pypi", allow_stan=True)
async def pypi(_, message: Message):
    BASE_URL = "https://pypi.org/pypi/{0}/json"
    if len(message.command) < 2:
        return await Arankbot.delete(message, "No package name provided!")

    package = message.command[1]
    Arank = await Arankbot.edit(message, "`getting information...`")

    response = requests.get(BASE_URL.format(package))
    if response.status_code == 200:
        data = response.json()
        info = data["info"]
        name = info["name"]
        url = info["package_url"]
        version = info["version"]
        summary = info["summary"]
        await Arank.edit(f"**𝖯𝖺𝖼𝗄𝖺𝗀𝖾:** [{name}]({url}) (`{version}`)\n\n**𝖣𝖾𝗍𝖺𝗂𝗅𝗌:** `{summary}`")
    else:
        await Arank.edit(f"**𝖯𝖺𝖼𝗄𝖺𝗀𝖾:** `{package}`\n\n**𝖣𝖾𝗍𝖺𝗂𝗅𝗌:** `Not Found`")


@on_message("speedtest", allow_stan=True)
async def speed_test(_, message: Message):
    Arank = await Arankbot.edit(message, "`testing speed...`")

    speed = Speedtest()
    speed.get_best_server()

    await Arank.edit("`calculating download speed...`")
    speed.download()

    await Arank.edit("`calculating upload speed...`")
    speed.upload()

    await Arank.edit("`finising up...`")
    speed.results.share()
    result = speed.results.dict()

    form = """**𝖲𝗉𝖾𝖾𝖽𝖳𝖾𝗌𝗍 𝖱𝖾𝗌𝗎𝗅𝗍𝗌 🍀**

    **✧ 𝖨𝖲𝖯:** `{0}, {1}` 
    **✧ 𝖯𝗂𝗇𝗀:** `{2}`
    **✧ 𝖲𝖾𝗋𝗏𝖾𝗋:** `{3}, {4}`
    **✧ 𝖲𝗉𝗈𝗇𝗌𝗈𝗋:** `{5}`
    """

    await message.reply_photo(
        result["share"],
        caption=form.format(
            result["client"]["isp"],
            result["client"]["country"],
            result["ping"],
            result["server"]["name"],
            result["server"]["country"],
            result["server"]["sponsor"],
        )
    )
    await Arank.delete()


HelpMenu("eval").add(
    "eval",
    "<python code>",
    "Execute the python code and get results.",
    "eval print('Aranko world')",
    "Use this command with caution! Using this command senselessly and getting yourself in trouble is not Arankbot's responsibility!"
).add(
    "exec",
    "<linux command>",
    "Execute the linux command and get results.",
    "exec ls -a",
    "Use this command with caution! Using this command senselessly and getting yourself in trouble is not Arankbot's responsibility!"
).add(
    "sArank",
    "<sArank script>",
    "Execute the sArank script and get results.",
    "sArank echo Aranko world",
    "Use this command with caution! Using this command senselessly and getting yourself in trouble is not Arankbot's responsibility!"
).add(
    "fext",
    "<file extention>",
    "Get the details of the file extention.",
    "fext py",
).add(
    "pypi",
    "<package name>",
    "Get the details of the package from pypi.",
    "pypi pyrogram",
).add(
    "speedtest",
    None,
    "Test the speed of server and client.",
    "speedtest",
).info(
    "Execute python, linux and sArank scripts."
).done()
