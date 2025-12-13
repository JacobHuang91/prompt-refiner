"""JSON cleaning and minification operations."""

import json
from typing import Any, Dict, List, Union

from ..refiner import Refiner


class JsonCleaner(Refiner):
    """
    Cleans and minifies JSON strings.
    Removes null values, empty containers, and extra whitespace.

    Args:
        strip_nulls: If True, remove null/None values from objects and arrays (default: True)
        strip_empty: If True, remove empty dicts, lists, and strings (default: True)

    Example:
        >>> from prompt_refiner import JsonCleaner
        >>> cleaner = JsonCleaner(strip_nulls=True, strip_empty=True)
        >>>
        >>> dirty_json = '''
        ... {
        ...   "name": "Alice",
        ...   "age": null,
        ...   "address": {},
        ...   "tags": [],
        ...   "bio": ""
        ... }
        ... '''
        >>> result = cleaner.run(dirty_json)
        >>> print(result)
        {"name":"Alice"}

    Use Cases:
        - **RAG Context Compression**: Strip nulls/empties from API responses before feeding to LLM
        - **Cost Optimization**: Reduce token count by removing unnecessary JSON structure
        - **Data Cleaning**: Normalize JSON from multiple sources with inconsistent null handling
    """

    def __init__(self, strip_nulls: bool = True, strip_empty: bool = True):
        """
        Initialize JSON cleaner.

        Args:
            strip_nulls: Remove null/None values
            strip_empty: Remove empty containers (dict, list, str)
        """
        self.strip_nulls = strip_nulls
        self.strip_empty = strip_empty

    def _clean_data(self, data: Any) -> Any:
        """
        Internal recursive cleaning logic.

        Args:
            data: Data structure to clean (dict, list, or primitive)

        Returns:
            Cleaned data structure
        """
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                cleaned_v = self._clean_data(v)

                # Check for nulls
                if self.strip_nulls and cleaned_v is None:
                    continue
                # Check for empty containers (dict/list/str)
                if self.strip_empty and isinstance(cleaned_v, (dict, list, str)) and not cleaned_v:
                    continue

                new_dict[k] = cleaned_v
            return new_dict

        elif isinstance(data, list):
            new_list = []
            for item in data:
                cleaned_item = self._clean_data(item)

                if self.strip_nulls and cleaned_item is None:
                    continue
                if (
                    self.strip_empty
                    and isinstance(cleaned_item, (dict, list, str))
                    and not cleaned_item
                ):
                    continue

                new_list.append(cleaned_item)
            return new_list

        return data

    def process(self, text: Union[str, Dict, List]) -> str:
        """
        Process the input JSON (string or object).
        Returns a minified JSON string.

        Args:
            text: JSON string, dict, or list to clean

        Returns:
            Minified JSON string with nulls/empties removed

        Note:
            If input is not valid JSON, returns input unchanged.
        """
        # 1. Parse Input (Handle both string JSON and raw Dict/List)
        data = text
        if isinstance(text, str):
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # If it's not valid JSON, return as-is to allow pipeline to continue safely
                return text

        # 2. Clean Structure
        cleaned_data = self._clean_data(data)

        # 3. Dump Minified String (No whitespace)
        return json.dumps(cleaned_data, ensure_ascii=False, separators=(",", ":"))
