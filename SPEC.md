# Contract specification

## Invariants

- The contract is non-payable and never transfers value.
- Campaign URLs and SHA-256 bindings are immutable after registration.
- Failed fetch, digest, or schema checks do not mutate lifecycle state.
- Only the publisher can activate its recall campaign.
- Any account may screen a batch against an active campaign.
- Duplicate batch digests within one campaign are rejected.
- Structured boundary fields are decided without an LLM.
- Unclear qualifier interpretation fails to `MANUAL_REVIEW`, never `AFFECTED`.
- Source text is treated as untrusted data and cannot expand the decision boundary.

## Closed source schemas

The exact keys accepted by each JSON document are enforced by `_recall` and `_batch`; unknown or missing keys are rejected. Lot suffixes are decimal and limited to 20 digits.
