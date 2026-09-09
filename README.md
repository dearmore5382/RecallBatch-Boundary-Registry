# RecallBatch Boundary Registry

A non-payable GenLayer dApp for answering one narrow question: does an authorized attestor's authenticated product batch fall inside an authorized publisher's recall boundary?

The contract first fetches exact JSON bytes under `strict_eq`, verifies caller-supplied SHA-256 digests, and validates closed schemas. Manufacturer, product, region, prefix, and numeric lot range are resolved deterministically. AI is used only when an authenticated recall contains a natural-language qualifier, and its output is bounded to `MATCH`, `NO_MATCH`, or `UNCLEAR`.

## Workflow

1. The owner manages explicit publisher and batch-attestor allowlists.
2. `register_recall(url, sha256)` creates an authorized publisher-owned campaign record.
3. `activate_recall(recall_id)` authenticates and freezes the recall source.
4. `screen_batch(recall_id, batch_url, batch_sha256)` requires an authorized attestor and an exact issuer/sender match.
5. Campaigns can be suspended or superseded; views expose authoritative registry state.

One campaign supports many screens. Duplicate prevention uses canonical manufacturer, product, region, and lot identity rather than mutable JSON bytes.

This is a boundary registry, not a safety, liability, refund, disposal, or legal-compliance determination.

## Verification

```bash
python -m pytest -q
npm test
npm run lint
npm run build
```

## Superseded deployment

`0xE36aE6FF03dFf98c81DA20d19A058e1c991960fc` and its audit demonstrate the earlier permissionless architecture only. It is not the current release and must not be submitted as current evidence. The hardened source requires a new deployment and fresh audit.
