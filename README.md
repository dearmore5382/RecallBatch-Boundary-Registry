# RecallBatch Boundary Registry

A non-payable GenLayer dApp for answering one narrow question: does an authenticated product batch fall inside an authenticated recall boundary?

The contract first fetches exact JSON bytes under `strict_eq`, verifies caller-supplied SHA-256 digests, and validates closed schemas. Manufacturer, product, region, prefix, and numeric lot range are resolved deterministically. AI is used only when an authenticated recall contains a natural-language qualifier, and its output is bounded to `MATCH`, `NO_MATCH`, or `UNCLEAR`.

## Workflow

1. `register_recall(url, sha256)` creates a publisher-owned campaign record.
2. `activate_recall(recall_id)` authenticates and freezes the official recall source.
3. `screen_batch(recall_id, batch_url, batch_sha256)` lets any account screen an independent authenticated batch against an active campaign.
4. `get_recall`, `get_screen`, and `get_counts` expose authoritative registry state.

One campaign supports many screens. A `(recall_id, batch_digest)` pair can only be screened once.

This is a boundary registry, not a safety, liability, refund, disposal, or legal-compliance determination.

## Verification

```bash
python -m pytest -q
npm test
npm run lint
npm run build
```

## Live deployment

- [Studionet contract](https://explorer-studio.genlayer.com/address/0xE36aE6FF03dFf98c81DA20d19A058e1c991960fc)
- [FINALIZED adversarial audit](verification/STUDIONET_AUDIT.md)
- [Sanitized machine-readable results](verification/live-0xe36ae6ff03dff98c81da20d19a058e1c991960fc.json)
