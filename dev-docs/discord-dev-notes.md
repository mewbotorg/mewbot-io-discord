<!--
SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: CC-BY-4.0
-->

# Running discord bot examples

## acquire a discord token

To run a bot on discord you need to acquire a bot token.
This is a string of numbers and letters which identifies your bot to discord when it tries to log in.

Tokens can have a number of different properties, or scopes.
These determine what you can do with a token.

I recommend following the [official discord guide](https://discordgsm.com/guide/how-to-get-a-discord-bot-token).
Which should walk you through the process.

Remember - if you want to view the contents of discord messages, you will need to enable the message content permission for the bot.
If you don't do this, all the message contents you see will be blank.

## prepare discord bot yaml

Now select the bot you want to actually run.
Each of the yaml files included in `examples\discord_bots` represents 

```yaml
kind: IOConfig
implementation: mewbot.io.discord.DiscordIO
uuid: aaaaaaaa-aaaa-4aaa-0000-aaaaaaaaaa00
properties:
  token: "[token goes here]"
  
---
```

Once you have prepared your token, paste it into the IOConfig block of the yaml for the bot you want to run.

The IOConfig block, for your token, should look something like

```yaml
kind: IOConfig
implementation: mewbot.io.discord.DiscordIO
uuid: aaaaaaaa-aaaa-4aaa-0000-aaaaaaaaaa00
properties:
  token: "a-series-of-letters-and-numbers-that-is-your-token"
  
---
```

Note the ``" "`` around your token.
This indicates, to the yaml, that your token should be treated as a string.
If you omit them, the yaml will be invalid and will not run.

### run the example - windows

Turning mewbot yaml into a bot is a fairly straightforward operation.

#### Through python and examples

You can use the code in the `__main__.py` file of examples.
Running something like 

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>python src\examples examples\discord_bots\history_discord_bot.yaml
```

#### Through the examples file in tools

You could also use the `sh` file found in the tools folder, running something like

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>sh tools/examples examples\discord_bots\history_discord_bot.yaml
```

NOTE - the direction of the `/` in `tools/examples`.
If you get it the wrong way round, `sh` would be able to interpret the path and you'll get an error like

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>sh tools\examples examples\discord_bots\history_discord_bot.yaml
tools\examples: line 7: tools\examples/path: Not a directory
tools\examples: line 9: exec: : not found
```

### run the example - linux

(I don't have a functioning linux box for this rn, so will fill this in later).

## DiscordIO Dev and Troubleshooting Notes

### Why am I getting blank events when messages are sent in channels the bot is monitoring?

As of late August 2022, discord bots now need the message content permission to be explicitly enabled (was implicitly enabled up to this point).
If this scope is not enabled all the messages will have null message content.
Enable the scope for the token via the developer portal and things should start working again.

### Pycord is not seeing events I expect it to

If you have enabled the appropriate scope for your bot via the developer token, and you are still not getting input events, you may need to update the intents in the __init__ of DiscordInput.
Currently they are set to `all` - but something might have altered here.

