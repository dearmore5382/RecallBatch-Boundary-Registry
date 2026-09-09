# Pre-deployment adversarial audit

## Happy path

- An activated campaign screens matching lot `240412` as `AFFECTED`.
- The same campaign independently screens lot `240950` as `NOT_AFFECTED`.
- The test replaces `_qualifier` with a function that throws, proving the empty-qualifier structured path does not invoke AI.

## Failure paths

- Wrong region and out-of-range lot produce `NOT_AFFECTED`.
- Non-publisher activation is rejected.
- One-byte recall drift produces `RECALL_HASH_MISMATCH` and leaves the campaign `REGISTERED`.

## Adversarial combinations

- Qualifier outputs `MATCH`, `NO_MATCH`, and `UNCLEAR` map to the three bounded verdicts.
- Re-screening the same batch digest in one campaign returns `DUPLICATE_SCREEN` without creating a record.
- Parser closes both schemas and bounds URLs, bodies, text, lists, attributes, and numeric suffix length.

Local evidence is not represented as live-chain evidence. Transaction hashes and explorer links remain pending until deployment.
