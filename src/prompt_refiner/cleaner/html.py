"""HTML stripping operation."""

import re
from typing import Optional, Set

from ..refiner import Refiner


class StripHTML(Refiner):
    """Remove HTML tags from text, with options to preserve semantic tags or convert to Markdown."""

    def __init__(
        self,
        preserve_tags: Optional[Set[str]] = None,
        to_markdown: bool = False,
    ):
        """
        Initialize the HTML stripper.

        Args:
            preserve_tags: Set of tag names to preserve (e.g., {'p', 'li', 'table'})
            to_markdown: Convert common HTML tags to Markdown syntax
        """
        self.preserve_tags = preserve_tags or set()
        self.to_markdown = to_markdown

    def process(self, text: str) -> str:
        """
        Remove HTML tags from the input text.

        Args:
            text: The input text containing HTML

        Returns:
            Text with HTML tags removed or converted to Markdown
        """
        result = text

        if self.to_markdown:
            # Convert common HTML tags to Markdown
            # Bold
            result = re.sub(r"<strong>(.*?)</strong>", r"**\1**", result, flags=re.DOTALL)
            result = re.sub(r"<b>(.*?)</b>", r"**\1**", result, flags=re.DOTALL)
            # Italic
            result = re.sub(r"<em>(.*?)</em>", r"*\1*", result, flags=re.DOTALL)
            result = re.sub(r"<i>(.*?)</i>", r"*\1*", result, flags=re.DOTALL)
            # Links
            result = re.sub(
                r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
                r"[\2](\1)",
                result,
                flags=re.DOTALL,
            )
            # Headers
            for i in range(1, 7):
                result = re.sub(
                    f"<h{i}[^>]*>(.*?)</h{i}>",
                    f"{'#' * i} \\1\n",
                    result,
                    flags=re.DOTALL,
                )
            # Code
            result = re.sub(r"<code>(.*?)</code>", r"`\1`", result, flags=re.DOTALL)
            # Lists - simple conversion
            result = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", result, flags=re.DOTALL)
            # Paragraphs
            result = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", result, flags=re.DOTALL)
            # Line breaks
            result = re.sub(r"<br\s*/?>", "\n", result)

        if self.preserve_tags:
            # Remove all tags except preserved ones
            # This is a simplified implementation
            tags_pattern = r"</?(?!" + "|".join(self.preserve_tags) + r"\b)[^>]+>"
            result = re.sub(tags_pattern, "", result)
        else:
            # Remove all HTML tags
            result = re.sub(r"<[^>]+>", "", result)

        # Clean up excessive newlines
        result = re.sub(r"\n{3,}", "\n\n", result)

        return result.strip()
