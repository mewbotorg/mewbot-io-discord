# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Provides an IOConfig for listening to and responding to discord message channels.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Set, Type

import logging

import discord
from mewbot.api.v1 import Input, InputEvent, InputQueue, IOConfig, Output, OutputEvent

from mewbot.io.discord.events import (
    DiscordInputEvent,
    DiscordMessageCreationEvent,
    DiscordMessageDeleteInputEvent,
    DiscordMessageEditInputEvent,
    DiscordOutputEvent,
    DiscordPostToChannelOutputEvent,
    DiscordReplyIntoMessageChannelOutputEvent,
    DiscordReplyToMessageOutputEvent,
    DiscordUserJoinInputEvent,
)

__version__ = "0.0.4"


class DiscordIO(IOConfig):
    """
    IOConfig for reading and writing to Discord.
    """

    _input: Optional[DiscordInput] = None
    _output: Optional[DiscordOutput] = None
    _token: str = ""
    _startup_queue_depth: int = 0
    _client: InternalMewbotDiscordClient

    @property
    def token(self) -> str:
        """
        The token this IOCofig is using to log into Discord.
        """
        return self._token

    @token.setter
    def token(self, token: str) -> None:
        self._token = token

    @property
    def startup_queue_depth(self) -> int:
        """
        On startup, this many messages will be retrieved and put on the wire.

        Messages will be retrieved from all channels this IOConfig is aware of.
        Note - this represents the TOTAL number of messages retrieved, not the PER CHANNEL number.
        There is currently no way to setting a per channel number.
        :return:
        """
        return self._startup_queue_depth

    @startup_queue_depth.setter
    def startup_queue_depth(self, startup_queue_depth: int) -> None:
        assert (
            startup_queue_depth >= 0
        ), "Please provide a positive (or 0) startup_queue_depth"
        self._startup_queue_depth = startup_queue_depth

    def get_inputs(self) -> Sequence[Input]:
        """
        Return the DiscordInput for this DiscordIO.
        """
        if not self._input:
            self._input = DiscordInput(self._token, self._startup_queue_depth)
            self._client = self._input.get_client()

        return [self._input]

    def get_outputs(self) -> Sequence[Output]:
        """
        Return the DiscordOutput for this DiscordIO.
        """
        if not self._output:
            self._output = DiscordOutput(active_client=self._client)

        return [self._output]


class DiscordInput(Input):
    """
    Uses py-cord as a backend to connect, receive and send messages to discord.
    """

    _logger: logging.Logger
    _token: str
    _startup_queue_depth: int
    _client: InternalMewbotDiscordClient

    def __init__(self, token: str, startup_queue_depth: int = 0) -> None:
        """
        Initialize the Discord Input.

        :param token: The token need to authenticate this bot to the discord server
        :param startup_queue_depth:
            During startup, the number of DiscordTextInputEvents to put on the wire
            (Other forms of event are not always possible).
        """
        assert startup_queue_depth >= 0, "Does not support a negative startup_queue_depth"

        super().__init__()

        intents = discord.Intents.all()
        self._client = InternalMewbotDiscordClient(intents=intents)
        self._token = token
        self._logger = logging.getLogger(__name__ + "DiscordInput")

        self._startup_queue_depth = startup_queue_depth

        self._client._logger = self._logger
        self._client._startup_queue_depth = self._startup_queue_depth
        self._client.queue = self.queue

    def bind(self, queue: InputQueue) -> None:
        """
        Bind the queues into this Input class.

        :param queue:
        :return:
        """
        self.queue = queue
        self._client.queue = queue

    def get_client(self) -> InternalMewbotDiscordClient:
        """
        Return the internal client which the Input uses to talk to discord.

        We need the client in the output to allow certain OutputEvents to affect discord.
        :return:
        """
        return self._client

    @staticmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
        """
        Defines the set of input events this Input class can produce.
        """
        return {
            DiscordUserJoinInputEvent,
            DiscordMessageCreationEvent,
            DiscordMessageEditInputEvent,
            DiscordMessageDeleteInputEvent,
        }

    async def run(self) -> None:
        """
        Fires up a discord client to run this service.

        Token needs to be set by this point.
        """
        self._logger.info("About to connect to Discord")

        await self._client.start(self._token)


class InternalMewbotDiscordClient(discord.Client):
    """
    Discord.Client with overrode methods to actually interact with mewbot.

    In particular, methods have been overridden to write events to the InputQueue when they occur.
    """

    _logger: logging.Logger
    _startup_queue_depth: int

    queue: Optional[InputQueue]

    async def on_ready(self) -> None:
        """
        Called once at the start, after the bot has connected to discord.
        """
        self._logger.info("%s has connected to Discord!", self.user)

        await self.retrieve_old_message()

    async def retrieve_old_message(self) -> None:
        """
        If a startup_queue_depth is set, then retrieve that number of entries and transmit them.
        """
        if not self._startup_queue_depth:
            return

        # Might want to, instead, wait for a queue
        if not self.queue:
            return

        self._logger.info("Retrieving %s old messages", self._startup_queue_depth)

        # The aim is to build a list of the last five messages the bot would have seen if it was up
        # - iterate over all the guilds the bot can see
        # - then iterate over all the text channels in that guild
        # - grab a number of messages equal to the queue depth
        # - append them to a master list
        # - sort on time in the master list
        # - return the queue depth number of items from the sorted list
        past_messages: List[discord.Message] = []

        # Shortcut for iterating over all guilds, then all channels
        for channel in self.get_all_channels():
            # Ignoring everything which is not a text channel - nothing to do with past voice
            if not isinstance(channel, discord.channel.TextChannel):
                continue

            messages = [x async for x in channel.history(limit=5)]
            past_messages.extend(messages)

        # Sort the messages and put the last five on the wire
        past_messages = sorted(
            past_messages, key=lambda x: float(x.created_at.timestamp()), reverse=True
        )

        for message in past_messages[: self._startup_queue_depth]:
            if not isinstance(message, discord.Message):
                self._logger.info("Expected a message and got a %s", type(message))

            await self.queue.put(
                DiscordMessageCreationEvent(text=message.content, message=message)
            )

    async def on_message(self, message: discord.Message) -> None:
        """
        Check for acceptance on all commands - execute the first one that matches.

        :param message:
        :return:
        """
        if not self.queue:
            return

        await self.queue.put(
            DiscordMessageCreationEvent(text=str(message.clean_content), message=message)
        )

    async def on_member_join(self, member: discord.Member) -> None:
        """
        Triggered when a member joins one of the guilds that the bot is monitoring.
        """
        self._logger.info(
            'New member "%s" has been detected joining"%s"',
            str(member.mention),
            str(member.guild.name),
        )

        if not self.queue:
            return

        await self.queue.put(DiscordUserJoinInputEvent(member=member))

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        """
        Triggered when a message is edited on any of the channels which the bot is monitoring.

        :param before: The message before the edit
        :param after: The message after the edit
        """
        self._logger.info("Message edit - %s changed to %s", before.content, after.content)

        if not self.queue:
            return

        await self.queue.put(
            DiscordMessageEditInputEvent(
                text_before=before.content,
                message_before=before,
                text_after=after.content,
                message_after=after,
            )
        )

    async def on_message_delete(self, message: discord.Message) -> None:
        """
        Triggered when a message is deleted on any of the channels which the bot is monitoring.

        :param message: The message before the delete event occurred.
        """
        self._logger.info(
            "Message delete - %s has deleted a message with content %s",
            message.author,
            message.content,
        )

        if not self.queue:
            return

        await self.queue.put(
            DiscordMessageDeleteInputEvent(text_before=message.content, message=message)
        )


class DiscordOutput(Output):
    """
    Output class to write events to connected Discord servers.
    """

    _client: InternalMewbotDiscordClient

    def __init__(self, active_client: InternalMewbotDiscordClient):
        """
        Initialise this class with a client to effect changes to discord beyond replying.

        :param active_client:
        """
        self._client = active_client

    @staticmethod
    def consumes_outputs() -> Set[Type[OutputEvent]]:
        """
        Defines the set of output events that this Output class can consume.
        """
        return {DiscordOutputEvent}

    async def output(self, event: OutputEvent) -> bool:
        """
        Does the work of transmitting the event to the world.

        :param event:
        :return:
        """

        if not isinstance(event, DiscordOutputEvent):
            return False

        if isinstance(event, DiscordReplyToMessageOutputEvent):
            return await self._process_reply_to_message(event)

        if isinstance(event, DiscordReplyIntoMessageChannelOutputEvent):
            return await self._process_reply_into_message_channel_event(event)

        if isinstance(event, DiscordOutputEvent):
            return await self._process_bare_event(event)

        if isinstance(event, DiscordPostToChannelOutputEvent):
            return await self._process_post_to_channel_output_evnet(event)

        raise NotImplementedError("Currently can only respond to a message")

    @staticmethod
    async def _process_reply_to_message(event: DiscordReplyToMessageOutputEvent) -> bool:
        """
        Process a DiscordReplyToMessageOutputEvent event.

        :param event:
        :return:
        """
        await event.message.reply(event.text)
        return True

    @staticmethod
    async def _process_reply_into_message_channel_event(
        event: DiscordReplyIntoMessageChannelOutputEvent,
    ) -> bool:
        """
        Reply into the same channel which produced the message.

        :param event:
        :return:
        """
        await event.message.channel.send(event.text)
        return True

    @staticmethod
    async def _process_bare_event(event: DiscordOutputEvent) -> bool:
        """
        Process a bare DiscordOutputEvent event.

        :param event:
        :return:
        """
        # Don't know how to send this message
        if event.message is None:
            return False

        await event.message.channel.send(event.text)
        return True

    async def _process_post_to_channel_output_evnet(
        self, event: DiscordPostToChannelOutputEvent
    ) -> bool:
        """
        Process a DiscordPostToChannelOutputEvent.

        This instructs the bot to post to an existing channel.
        :param event:
        :return:
        """
        channel_id = event.channel_id

        channel = self._client.get_channel(channel_id)
        if channel is None:
            return False
        if isinstance(channel, (discord.abc.PrivateChannel, discord.abc.GuildChannel)):
            return False

        await channel.send(event.text)

        return True


__all__ = [
    "DiscordInputEvent",
    "DiscordMessageCreationEvent",
    "DiscordMessageDeleteInputEvent",
    "DiscordMessageEditInputEvent",
    "DiscordOutputEvent",
    "DiscordUserJoinInputEvent",
    "DiscordIO",
    "DiscordInput",
    "DiscordOutput",
    "DiscordReplyIntoMessageChannelOutputEvent",
    "DiscordReplyToMessageOutputEvent",
]
