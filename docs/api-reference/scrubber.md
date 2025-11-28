# Scrubber Module

The Scrubber module provides operations for security and privacy, including automatic PII redaction.

## RedactPII

Redact sensitive personally identifiable information (PII) from text using regex patterns.

::: prompt_refiner.scrubber.RedactPII
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Supported PII Types

- **`email`**: Email addresses → `[EMAIL]`
- **`phone`**: Phone numbers (US format) → `[PHONE]`
- **`ip`**: IP addresses → `[IP]`
- **`credit_card`**: Credit card numbers → `[CARD]`
- **`ssn`**: Social Security Numbers → `[SSN]`
- **`url`**: URLs → `[URL]`

### Examples

```python
from prompt_refiner import RedactPII

# Redact all PII types
redactor = RedactPII()
result = redactor.process("Contact me at john@example.com or 555-123-4567")
# Output: "Contact me at [EMAIL] or [PHONE]"

# Redact specific types only
redactor = RedactPII(redact_types={"email", "phone"})
result = redactor.process("Email: john@example.com, IP: 192.168.1.1")
# Output: "Email: [EMAIL], IP: 192.168.1.1"

# Custom patterns
redactor = RedactPII(
    custom_patterns={"employee_id": r"EMP-\d{5}"}
)
result = redactor.process("Employee EMP-12345 accessed the system")
# Output: "Employee [EMPLOYEE_ID] accessed the system"

# Custom keywords (case-insensitive)
redactor = RedactPII(
    custom_keywords={"confidential", "secret"}
)
result = redactor.process("This is Confidential information")
# Output: "This is [REDACTED] information"
```

### Combining Options

```python
from prompt_refiner import RedactPII

# Redact standard PII + custom patterns + keywords
redactor = RedactPII(
    redact_types={"email", "phone", "ssn"},
    custom_patterns={"employee_id": r"EMP-\d{5}"},
    custom_keywords={"internal", "confidential"}
)

text = """
Employee EMP-12345
Email: john@example.com
Phone: 555-123-4567
SSN: 123-45-6789
This is Confidential information for internal use only.
"""

result = redactor.process(text)
```

## Common Use Cases

### Before Sending to LLM APIs

```python
from prompt_refiner import Refiner, RedactPII

secure_pipeline = (
    Refiner()
    .pipe(RedactPII(redact_types={"email", "phone", "ssn", "credit_card"}))
)

# Safe to send to external APIs
secure_text = secure_pipeline.run(user_input)
```

### Logging and Monitoring

```python
from prompt_refiner import Refiner, RedactPII

log_redactor = (
    Refiner()
    .pipe(RedactPII())  # Redact all PII types
)

# Safe to log
safe_log = log_redactor.run(sensitive_data)
logger.info(safe_log)
```

### Data Export Compliance

```python
from prompt_refiner import Refiner, RedactPII

# Custom redaction for specific compliance needs
gdpr_redactor = (
    Refiner()
    .pipe(RedactPII(
        redact_types={"email", "phone", "ip"},
        custom_keywords={"customer_name", "address", "dob"}
    ))
)

export_data = gdpr_redactor.run(user_data)
```

## Security Best Practices

!!! warning "Regex Limitations"
    PII redaction uses regex patterns which may not catch all variations. For production use:

    - Test thoroughly with your specific data
    - Consider using specialized PII detection services for critical applications
    - Add custom patterns for domain-specific PII
    - Review redacted output before sending to external services

!!! tip "Defense in Depth"
    PII redaction is one layer of security. Always:

    - Validate and sanitize user input
    - Use proper authentication and authorization
    - Encrypt data in transit and at rest
    - Follow your organization's security policies
