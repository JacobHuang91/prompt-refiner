# Custom Operations

Create your own operations to extend Prompt Refiner.

## Creating a Custom Operation

All operations inherit from the `Operation` base class and implement the `process` method:

```python
from prompt_refiner import Operation

class RemoveEmojis(Operation):
    """Remove emoji characters from text."""

    def process(self, text: str) -> str:
        import re
        # Simple emoji removal pattern
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub("", text)
```

## Using Your Custom Operation

Use it like any built-in operation:

```python
from prompt_refiner import Refiner, NormalizeWhitespace

pipeline = (
    Refiner()
    .pipe(RemoveEmojis())
    .pipe(NormalizeWhitespace())
)

result = pipeline.run("Hello 😀 World 🌍!")
# Output: "Hello World !"
```

## More Examples

### Remove URLs

```python
import re
from prompt_refiner import Operation

class RemoveURLs(Operation):
    def process(self, text: str) -> str:
        url_pattern = r'https?://\S+|www\.\S+'
        return re.sub(url_pattern, '[URL]', text)
```

### Lowercase Text

```python
from prompt_refiner import Operation

class Lowercase(Operation):
    def process(self, text: str) -> str:
        return text.lower()
```

### Remove Numbers

```python
import re
from prompt_refiner import Operation

class RemoveNumbers(Operation):
    def process(self, text: str) -> str:
        return re.sub(r'\d+', '', text)
```

## Guidelines

1. **Single responsibility** - Each operation should do one thing well
2. **Immutable** - Don't modify the input, return a new string
3. **Deterministic** - Same input should always produce same output
4. **Document** - Add docstrings explaining what it does

## Contributing

Have a useful operation? Consider contributing it to Prompt Refiner!

[See contributing guide →](../contributing.md){ .md-button }
