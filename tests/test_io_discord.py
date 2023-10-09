# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""Testing loading a DiscordIO from YAML definition."""

from __future__ import annotations

from typing import Type

from mewbot.api.v1 import IOConfig
from mewbot.test import BaseTestClassWithConfig

from mewbot.io.discord import DiscordIO

# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestIoHttpsPost(BaseTestClassWithConfig[DiscordIO]):
    """Testing loading a DiscordIO from YAML definition."""

    config_file: str = "examples/discord_bots/trivial_discord_bot.yaml"
    implementation: Type[DiscordIO] = DiscordIO

    def test_check_class(self) -> None:
        """Testing loading a DiscordIO from YAML definition."""

        assert isinstance(self.component, DiscordIO)
        assert isinstance(self.component, IOConfig)
