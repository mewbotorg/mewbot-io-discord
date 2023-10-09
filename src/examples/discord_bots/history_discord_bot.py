#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable
# Aims to expose the full capabilities of this discord bot framework

"""
Provides supporting pyton functions for the history_discord_bot.yaml example.

This demonstrates that the DiscordIO config can retrieve a set number of discord events from
the past when the bot starts up.
Note - would be nice to set a number per channel as well as a global number.
"""


from __future__ import annotations

from typing import Any, AsyncIterable, Dict, Set, Type

import logging

from mewbot.api.v1 import Action, Trigger
from mewbot.core import InputEvent, OutputEvent, OutputQueue

from mewbot.io.discord import (
    DiscordInputEvent,
    DiscordMessageCreationEvent,
    DiscordMessageEditInputEvent,
    DiscordOutputEvent,
)


class DiscordAllCommandTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is a DiscordTextInputEvent - of any type.
    """

    _command: str = ""

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Input Events this trigger can respond to.

        In particular, when a message is created or edited.
        (Note - this, perhaps, should be expanded or the class renamed).
        """
        return {DiscordMessageCreationEvent, DiscordMessageEditInputEvent}

    @property
    def command(self) -> str:
        """
        Not currently in use - should be removed.
        """
        return self._command

    @command.setter
    def command(self, command: str) -> None:
        self._command = str(command)

    def matches(self, event: InputEvent) -> bool:
        """
        Tests if the given Input Event match the criteria of this trigger.

        In particular - is it Discord Input Event?
        :param event:
        :return:
        """
        if not isinstance(event, DiscordInputEvent):
            return False

        return True


class DiscordPrintAction(Action):
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
        Input Events this Action can respond to.
        """
        return {DiscordMessageCreationEvent, DiscordMessageEditInputEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        Output events this Action can produce in response to Inputs.

        In particular, will always be a Discord Output Event of some sort.
        :return:
        """
        return {DiscordOutputEvent}

    @property
    def message(self) -> str:
        """
        Not actually in use - should probably be removed.
        """
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = str(message)

    async def act(self, event: InputEvent, state: Dict[str, Any]) -> AsyncIterable[None]:
        """
        Construct a DiscordOutputEvent with the result of performing the calculation.
        """
        print(event)
        yield None
