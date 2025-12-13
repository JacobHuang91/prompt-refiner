"""Example: Redacting PII (Personally Identifiable Information)."""

from prompt_refiner import Pipeline, RedactPII

# Customer support ticket with PII
support_ticket = """
Customer Support Ticket #12345

Customer: John Doe
Email: john.doe@example.com
Phone: 555-123-4567
IP Address: 192.168.1.100

Issue Description:
I tried to access https://app.example.com/dashboard but got an error.
My credit card 4532-1234-5678-9010 was charged but the service didn't activate.
Please help urgently!

SSN for verification: 123-45-6789
"""

print("=" * 60)
print("PII REDACTION EXAMPLE")
print("=" * 60)
print(f"\nOriginal ticket:\n{support_ticket}")

# Example 1: Redact all PII types
print("\n" + "-" * 60)
print("Full PII redaction (all types)")
print("-" * 60)
refiner = Pipeline().pipe(RedactPII())
redacted = refiner.run(support_ticket)
print(f"Result:\n{redacted}")

# Example 2: Selective redaction (only email and phone)
print("\n" + "-" * 60)
print("Selective redaction (email and phone only)")
print("-" * 60)
refiner_selective = Pipeline().pipe(RedactPII(redact_types={"email", "phone"}))
redacted_selective = refiner_selective.run(support_ticket)
print(f"Result:\n{redacted_selective}")

# Example 3: Custom patterns and keywords
internal_doc = """
Project CLASSIFIED: New AI initiative
Lead: alice@company.internal
Server: 10.0.0.50
Budget: CONFIDENTIAL

This SECRET project involves developing proprietary algorithms.
"""

print("\n" + "-" * 60)
print("Custom patterns and keywords")
print("-" * 60)
print(f"\nOriginal document:\n{internal_doc}")

refiner_custom = Pipeline().pipe(
    RedactPII(
        redact_types={"email", "ip"},
        custom_keywords={"classified", "secret", "confidential", "proprietary"},
    )
)
redacted_custom = refiner_custom.run(internal_doc)
print(f"\nRedacted document:\n{redacted_custom}")
