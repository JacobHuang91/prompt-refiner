# Scrubber Module

Protect sensitive information with automatic PII redaction.

## RedactPII Operation

Automatically redact personally identifiable information using regex patterns.

### Supported PII Types

- `email` - Email addresses
- `phone` - Phone numbers
- `ip` - IP addresses
- `credit_card` - Credit card numbers
- `ssn` - Social Security Numbers
- `url` - URLs

### Basic Usage

```python
from prompt_refiner import RedactPII

# Redact all PII types
redactor = RedactPII()
result = redactor.process("Contact john@example.com or 555-123-4567")
# Output: "Contact [EMAIL] or [PHONE]"

# Redact specific types
redactor = RedactPII(redact_types={"email", "phone"})
```

### Custom Patterns

```python
redactor = RedactPII(
    custom_patterns={"employee_id": r"EMP-\d{5}"}
)
```

[Full API Reference →](../api-reference/scrubber.md){ .md-button }
[View Examples](../examples/pii-redaction.md){ .md-button }
