#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable
# A minimum viable discord bot - which just responds with a set message to every input

"""
Provides python support functions for the trivial_discord_bot.yaml bot example.

This is trivial bot which listens to all channels it has access to.
In the even that it detects a message matching a string given in the yaml it will respond with a
string also given in the yaml.
"""


from __future__ import annotations

from typing import Any, AsyncIterable, Dict, Set, Type

import logging

from mewbot.api.v1 import Action, Trigger
from mewbot.core import InputEvent, OutputEvent, OutputQueue

from mewbot.io.discord import DiscordMessageCreationEvent, DiscordOutputEvent


class DiscordTextCommandTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is a DiscordTextInputEvent.
    """

    _command: str = ""

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Inputs this Trigger could respond to.

        In particular, it will be passed any Discord Message Creation Events.
        (Though it may or may not respond to them - that will depend if the message passes the
        matches criteria).
        :return:
        """
        return {DiscordMessageCreationEvent}

    @property
    def command(self) -> str:
        """
        If a message body matched this command string, the trigger will fire.
        """
        return self._command

    @command.setter
    def command(self, command: str) -> None:
        self._command = str(command)

    def matches(self, event: InputEvent) -> bool:
        """
        If the event is a Discord Message Creation Event, and the text matches, it will pass.

        Text is set as "command" in the yaml.
        Method will only pass (return True) if the text of the message exactly matches that in the
        command field of the yaml.
        :param event:
        :return:
        """
        if not isinstance(event, DiscordMessageCreationEvent):
            return False

        return event.text == self._command


class DiscordCommandTextResponse(Action):
    """
    Print every InputEvent.
    """

    _logger: logging.Logger
    _queue: OutputQueue
    _message: str = ""

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + type(self).__name__)

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Input Event types this Action will respond to.
        """
        return {DiscordMessageCreationEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        Output Event types this method can produce.
        """
        return {DiscordOutputEvent}

    @property
    def message(self) -> str:
        """
        Response str to a message which passes selection.

        When a discord message in a monitored channel is detected which matches the command string,
        this message will be sent in response to it.
        :return:
        """
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = str(message)

    async def act(
        self, event: InputEvent, state: Dict[str, Any]
    ) -> AsyncIterable[OutputEvent]:
        """
        Construct a DiscordOutputEvent with the result of performing the calculation.
        """
        if not isinstance(event, DiscordMessageCreationEvent):
            self._logger.warning("Received wrong event type %s", type(event))
            return

        test_event = DiscordOutputEvent(
            text=self._message, message=event.message, use_message_channel=True
        )

        yield test_event
