"""Example: Creating a custom operation."""

from prompt_groomer import Groomer, NormalizeWhitespace
from prompt_groomer.operation import Operation


class RemoveEmojis(Operation):
    """Custom operation to remove emoji characters."""

    def process(self, text: str) -> str:
        """Remove emoji characters from text."""
        # Simple emoji removal (basic implementation)
        import re

        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.sub("", text)


class UpperCase(Operation):
    """Custom operation to convert text to uppercase."""

    def process(self, text: str) -> str:
        """Convert text to uppercase."""
        return text.upper()


# Use custom operations in a pipeline
groomer = (
    Groomer()
    .pipe(RemoveEmojis())
    .pipe(NormalizeWhitespace())
    .pipe(UpperCase())
)

text_with_emojis = "Hello 👋 world 🌍 this is awesome! 🎉"

result = groomer.run(text_with_emojis)

print("Original:")
print(text_with_emojis)
print("\nAfter custom pipeline:")
print(result)
