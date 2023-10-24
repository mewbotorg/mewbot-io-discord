#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable
# Aims to expose the full capabilities of this discord bot framework

"""
Provides python support functions for the delete_warn_discord_bot.yaml example.

This is a Bot which warns the user when there has been a message deletion event in any of the
channels which this bot has access to.
If message is in the discord cache, then the message contents that where deleted will also be
provided.
"""


from __future__ import annotations

from typing import Any, AsyncIterable, Dict, Set, Type

import logging

from mewbot.api.v1 import Action, Trigger
from mewbot.core import InputEvent, OutputEvent, OutputQueue

from mewbot.io.discord import DiscordMessageDeleteInputEvent, DiscordOutputEvent


class DiscordDeleteEventTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is a DiscordDeleteEvent.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Inputs this method responds to.

        This will only pass on message deletion input events.
        :return:
        """
        return {
            DiscordMessageDeleteInputEvent,
        }

    def matches(self, event: InputEvent) -> bool:
        """
        Will only match, and so trigger, on message deletion input events.

        :param event:
        :return:
        """
        if isinstance(event, DiscordMessageDeleteInputEvent):
            return True

        return False


class DiscordDeleteResponseAction(Action):
    """
    Respond to every deletion event in the channel where the message was located.
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
        This Action will only act on message deletion events.
        """
        return {
            DiscordMessageDeleteInputEvent,
        }

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        Output Events that this action can produce.
        """
        return {DiscordOutputEvent}

    @property
    def message(self) -> str:
        """
        Message for this warning should be provided as a static string.

        Note - not sure this is currently used!
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
        if not isinstance(event, DiscordMessageDeleteInputEvent):
            self._logger.warning("Received wrong event type %s", type(event))
            return

        self._logger.info("We have detected deleting! - %s", event)
        test_event = DiscordOutputEvent(
            text=f'User {event.message.author} has deleted message: "{event.message.content}"',
            message=event.message,
        )
        yield test_event
