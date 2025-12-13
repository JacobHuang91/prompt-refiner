"""Unicode normalization and cleanup operation."""

import unicodedata

from ..refiner import Refiner


class FixUnicode(Refiner):
    """Remove or fix problematic Unicode characters."""

    def __init__(self, remove_zero_width: bool = True, remove_control_chars: bool = True):
        """
        Initialize the Unicode fixer.

        Args:
            remove_zero_width: Remove zero-width spaces and similar characters
            remove_control_chars: Remove control characters (except newlines and tabs)
        """
        self.remove_zero_width = remove_zero_width
        self.remove_control_chars = remove_control_chars

    def process(self, text: str) -> str:
        """
        Clean problematic Unicode characters from text.

        Args:
            text: The input text

        Returns:
            Text with problematic Unicode characters removed
        """
        result = text

        if self.remove_zero_width:
            # Remove zero-width characters
            zero_width_chars = [
                "\u200b",  # Zero-width space
                "\u200c",  # Zero-width non-joiner
                "\u200d",  # Zero-width joiner
                "\ufeff",  # Zero-width no-break space (BOM)
                "\u2060",  # Word joiner
            ]
            for char in zero_width_chars:
                result = result.replace(char, "")

        if self.remove_control_chars:
            # Remove control characters except newlines, tabs, and carriage returns
            # Keep: \n (0x0A), \t (0x09), \r (0x0D)
            result = "".join(
                char
                for char in result
                if not unicodedata.category(char).startswith("C") or char in ("\n", "\t", "\r")
            )

        # Normalize Unicode to NFC form (canonical composition)
        result = unicodedata.normalize("NFC", result)

        return result
