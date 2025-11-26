# PII Redaction Example

Automatically redact sensitive information before sending to APIs.

## Scenario

User input contains personal information that should not be sent to external LLM APIs.

## Example Code

```python
from prompt_groomer import Groomer, RedactPII

user_input = """
Please contact me at john.doe@example.com or call 555-123-4567.
My account number is EMP-12345.
"""

groomer = Groomer().pipe(RedactPII())
secure = groomer.run(user_input)

print(secure)
# Output:
# Please contact me at [EMAIL] or call [PHONE].
# My account number is EMP-12345.
```

## Custom Patterns

```python
groomer = Groomer().pipe(RedactPII(
    redact_types={"email", "phone"},
    custom_patterns={"employee_id": r"EMP-\d{5}"}
))

secure = groomer.run(user_input)
# Now EMP-12345 is also redacted as [EMPLOYEE_ID]
```

## Full Example

See: [`examples/scrubber/pii_redaction.py`](https://github.com/JacobHuang91/prompt-groomer/blob/main/examples/scrubber/pii_redaction.py)

## Related

- [RedactPII API Reference](../api-reference/scrubber.md)
- [Scrubber Module Guide](../modules/scrubber.md)
