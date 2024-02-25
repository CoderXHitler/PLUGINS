# ArankBot v3 Plugins

# Follow this format to make your own plugin for ArankBot.

```python3
"""
A sample code to display Aranko without taking input.
"""
# this is a mandatory import
from . import on_message, Arankbot, HelpMenu

# assigning command
@on_message("hii")
async def hi(_, message):
    # command body
    await Arankbot.edit(message, "Aranko!")


# to display in help menu
HelpMenu("hii").add(
  "hii", None, "Says Aranko!"
).done()
```

```python3
"""
A sample code to display Aranko with input.
"""
# this is a mandatory import
from . import on_message, Arankbot, HelpMenu

# assigning command
@on_message("hii", allow_stan=True)
async def hi(_, message):
    # command body
    msg = await Arankbot.input(message)
    if msg:
        await Arankbot.edit(message, f"Aranko! {msg}")
    else:
        await Arankbot.edit(message, "Aranko!")


# to display in help menu
HelpMenu("hii").add(
    "hii", "<text>", "Display Aranko with a input!"
).done()
```


## To get more functions read codes in repo.
