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

## Current hardened deployment

- [Studionet contract](https://explorer-studio.genlayer.com/address/0x1E09EDDbd1dde3eC95f150D02304f542d511132F)
- [Hardened FINALIZED audit](verification/HARDENED_STUDIONET_AUDIT.md)
- [Sanitized machine-readable results](verification/live-0x1e09eddbd1dde3ec95f150d02304f542d511132f.json)
- [Exact source-parity result](verification/preflight-0x1e09eddbd1dde3ec95f150d02304f542d511132f.json)

The earlier permissionless contract `0xE36a…60fc` is superseded and is retained only as historical evidence.
