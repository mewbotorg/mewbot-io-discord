# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Events which your IOConfig can produce/consume.
"""

import dataclasses

import discord
from mewbot.api.v1 import InputEvent, OutputEvent


@dataclasses.dataclass
class DiscordInputEvent(InputEvent):
    """
    Base class for an event occurring on a monitored discord server.
    """


@dataclasses.dataclass
class DiscordUserJoinInputEvent(DiscordInputEvent):
    """
    Class which represents a user joining one of the discord channels which the bot has access to.
    """

    member: discord.member.Member


@dataclasses.dataclass
class DiscordMessageCreationEvent(DiscordInputEvent):
    """
    A discord message has been created in a channel on a server the bot monitors.
    """

    text: str
    message: discord.Message


@dataclasses.dataclass
class DiscordMessageEditInputEvent(DiscordInputEvent):
    """
    A discord message has been edited in a channel on a server the bot monitors.
    """

    text_before: str
    message_before: discord.Message

    text_after: str
    message_after: discord.Message


@dataclasses.dataclass
class DiscordMessageDeleteInputEvent(DiscordInputEvent):
    """
    A discord message has been deleted in a channel on a server the bot monitors.
    """

    text_before: str
    message: discord.Message


@dataclasses.dataclass
class DiscordOutputEvent(OutputEvent):
    """
    Currently just used to reply to an input event.
    """

    text: str
    message: discord.Message
    use_message_channel: bool
    reply_to_triggering_message: bool = False
