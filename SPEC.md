# Contract specification

## Invariants

- The contract is non-payable and never transfers value.
- The deployer is owner and initially holds publisher and attestor roles.
- Only the owner can grant or revoke roles.
- Campaign URLs and SHA-256 bindings are immutable after registration.
- Failed fetch, digest, or schema checks do not mutate lifecycle state.
- Only the publisher can activate its recall campaign.
- Only allowlisted attestors may screen, and the authenticated batch issuer must equal the transaction sender.
- Duplicate canonical batch identities within one campaign are rejected even if URLs, JSON formatting, digest, reference, or issuer change.
- An active campaign can be suspended; an active or suspended campaign can be superseded by another active campaign from the same publisher.
- Structured boundary fields are decided without an LLM.
- `NO_MATCH`, `UNCLEAR`, malformed, or failed qualifier interpretation fails to `MANUAL_REVIEW`; AI can never create `NOT_AFFECTED`.
- Source text is treated as untrusted data and cannot expand the decision boundary.

## Closed source schemas

The exact keys accepted by each JSON document are enforced by `_recall` and `_batch`; unknown or missing keys are rejected. Lot suffixes are decimal and limited to 20 digits.
