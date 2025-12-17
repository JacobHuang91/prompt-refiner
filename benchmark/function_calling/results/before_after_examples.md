# Response Compression Examples

Top 3 API responses by token reduction percentage:

## 19. stripe_payment_response

**Token Reduction**: 923 → 437 (52.7% reduction)

**Category**: Complex

**Compression Results**:
- Original keys: 44
- Compressed keys: 23
- Keys removed: 21
- Size reduction: 2645 → 1230 bytes

**Removed Debug Fields**: amount_details, application, application_fee_amount, automatic_payment_methods, canceled_at, cancellation_reason, invoice, last_payment_error, next_action, on_behalf_of, payment_method_configuration_details, processing, review, setup_future_usage, shipping, source, statement_descriptor, statement_descriptor_suffix, transfer_data, transfer_group, logs

**Essential Fields Preserved** (showing first 5): id, object, amount, amount_capturable, amount_received

---

## 18. slack_send_message_response

**Token Reduction**: 608 → 396 (34.9% reduction)

**Category**: Complex

**Compression Results**:
- Original keys: 9
- Compressed keys: 8
- Keys removed: 1
- Size reduction: 1886 → 1191 bytes

**Removed Debug Fields**: logs

**Essential Fields Preserved** (showing first 5): ok, channel, ts, message, response_metadata

---

## 11. openai_calculator_response

**Token Reduction**: 521 → 347 (33.4% reduction)

**Category**: Complex

**Compression Results**:
- Original keys: 13
- Compressed keys: 12
- Keys removed: 1
- Size reduction: 1489 → 972 bytes

**Removed Debug Fields**: logs

**Essential Fields Preserved** (showing first 5): operation, operands, result, result_formatted, precision

---

