#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable

"""
Provides pyton support functions for the discord_to_desktop_notification.yaml example bot.

Trivial example of a bot to trigger a desktop notification whenever a message with certain contents
is detected in any of the channels which this bot has access to.
"""

from __future__ import annotations

from typing import Any, AsyncIterable, Dict, Set, Type

import logging

from mewbot.api.v1 import Action, Trigger
from mewbot.core import InputEvent, OutputEvent, OutputQueue
from mewbot.io.desktop_notification import DesktopNotificationOutputEvent

from mewbot.io.discord import DiscordMessageCreationEvent


class DiscordTextCommandTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is a DiscordTextInputEvent.
    """

    _command: str = ""

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Input events this Trigger will respond to at all.

        These events might, or might not, actually pass the trigger.
        But only events of these types will be responded to at all.
        In this case, event has to be a Message Creation Event, or it will be ignored completely.
        """
        return {DiscordMessageCreationEvent}

    @property
    def command(self) -> str:
        """
        The command str to trigger the desktop notification with.

        The command this function will respond to can be customized in yaml.
        Any message with contents which matches this will trigger a desktop notification.
        E.g. if the command was "ping" anyone entering a message with only the contents "ping"
        in a monitored discord channel would trigger a desktop notification.
        :return:
        """
        return self._command

    @command.setter
    def command(self, command: str) -> None:
        self._command = str(command)

    def matches(self, event: InputEvent) -> bool:
        """
        Checks that the message is something this trigger should respond to.

        Checks that the event is a Discord message creation event.
        Also checks that the contents of the message - its text - corresponds to the activation
        command set in the bot yaml.
        :param event:
        :return:
        """
        if not isinstance(event, DiscordMessageCreationEvent):
            return False

        return event.text == self._command


class DiscordMessageToNotificationAction(Action):
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
        Inputs that this action can react to.
        """
        return {DiscordMessageCreationEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        Event types this action can produce.

        Currently, only a DesktopNotificationOutputEvent.
        An event which will produce a desktop notification on the current system.
        :return:
        """
        return {DesktopNotificationOutputEvent}

    @property
    def message(self) -> str:
        """
        Message to be included in the desktop notification.

        (Usually these have two parts - the message body and the title - this will set the message
        body).
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

        test_event = DesktopNotificationOutputEvent(
            title="Someone said hello!",
            text=self._message,
        )
        self._logger.info("Triggering DesktopNotification %s", test_event)

        yield test_event
