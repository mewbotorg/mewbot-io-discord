"""
Tests for various utils.
"""

from mewbot.io.discord.utils import split_text


class TestMessagerChunker:
    """
    Tests the message chunker util - which chunks up messages.
    """

    def test_split_text_rwe(self) -> None:
        """
        Tests that the split_text function runs without throwing an error.

        :return:
        """
        assert isinstance(split_text("This is some text", 2000), list)

    def test_split_text_short_string_single_newline(self) -> None:
        """
        Tests splitting some short text with a single newline.

        :return:
        """
        test_text = "This is not very much text\nand the newline does not add much"

        assert split_text(test_text) == [
            test_text,
        ]
