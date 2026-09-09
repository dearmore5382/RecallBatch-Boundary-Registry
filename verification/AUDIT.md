# Hardened release pre-deployment adversarial audit

## Happy path

- Owner-authorized publisher activation and owner-authorized attestor screening succeed.
- An activated campaign screens matching lot `240412` as `AFFECTED`.
- The same campaign independently screens lot `240950` as `NOT_AFFECTED`.
- The test replaces `_qualifier` with a function that throws, proving the empty-qualifier structured path does not invoke AI.

## Failure paths

- Wrong region and out-of-range lot produce `NOT_AFFECTED`.
- Untrusted publishing and screening are rejected before source fetch.
- Non-publisher activation is rejected.
- Issuer/sender mismatch is rejected without state mutation.
- One-byte recall drift produces `RECALL_HASH_MISMATCH` and leaves the campaign `REGISTERED`.

## Adversarial combinations

- Qualifier outputs `MATCH`, `NO_MATCH`, and `UNCLEAR` map to the three bounded verdicts.
- Re-screening the same canonical batch identity after whitespace or reference changes returns `DUPLICATE_SCREEN`.
- Suspend and supersede transitions are authority- and state-gated.
- AI `NO_MATCH` and `UNCLEAR` both fail closed to `MANUAL_REVIEW`, never `NOT_AFFECTED`.
- Parser closes both schemas and bounds URLs, bodies, text, lists, attributes, and numeric suffix length.

Local evidence is not represented as live-chain evidence. Transaction hashes and explorer links remain pending until deployment.
