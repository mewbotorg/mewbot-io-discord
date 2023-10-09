#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable
# Aims to expose the full capabilities of this discord bot framework

"""
Provides python support functions for the editor_warn_discord_bot.yaml example bot.

Bot which warns the user when there has been a message edit event in any of the channels which
this bot has access to.
If message is in the discord cache, then the message contents before they were edited will be
provided, along with the current contents of the message.
"""

from __future__ import annotations

from typing import Any, AsyncIterable, Dict, Set, Type

import logging

from mewbot.api.v1 import Action, Trigger
from mewbot.core import InputEvent, OutputEvent, OutputQueue

from mewbot.io.discord import DiscordMessageEditInputEvent, DiscordOutputEvent


class DiscordEditTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is a DiscordEditInputEvent.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Inputs which will be examined by this trigger.
        """
        return {
            DiscordMessageEditInputEvent,
        }

    def matches(self, event: InputEvent) -> bool:
        """
        Matches, and so triggers, on all discord message edit input events.

        :param event:
        :return:
        """
        if isinstance(event, DiscordMessageEditInputEvent):
            return True

        return False


class DiscordEditResponse(Action):
    """
    Responds to every edit event in the channel where it occured.
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
        Input Events this Action can - theoretically - respond to.
        """
        return {
            DiscordMessageEditInputEvent,
        }

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        Output Events this Action can produce.
        """
        return {DiscordOutputEvent}

    @property
    def message(self) -> str:
        """
        Not currently in use - should be removed.
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
        if not isinstance(event, DiscordMessageEditInputEvent):
            self._logger.warning("Received wrong event type %s", type(event))
            return

        self._logger.info("We have detected editing! - %s", event)
        test_event = DiscordOutputEvent(
            text=f'We have detected editing! "{event.message_before.content}"'
            f' was changed to "f{event.message_after.content}"',
            message=event.message_after,
            use_message_channel=True,
        )
        yield test_event
