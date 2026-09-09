# Studionet adversarial audit

- Contract: [`0xE36aE6FF03dFf98c81DA20d19A058e1c991960fc`](https://explorer-studio.genlayer.com/address/0xE36aE6FF03dFf98c81DA20d19A058e1c991960fc)
- Exact deployed/local SHA-256: `bc4468e5d93b6682d40f511e6d09cba8cdb244027a91cf7c584ad40a908ec979`
- Fixture commit: [`c8f3f477`](https://github.com/dearmore5382/RecallBatch-Boundary-Registry/tree/c8f3f47789acf6f44822f3620f7c96ad59ec9692/test-fixtures)
- Final state: one active campaign, two immutable screens.

| Case | Expected/actual | FINALIZED transaction |
|---|---|---|
| Invalid hash is rejected atomically | `INVALID_SOURCE_HASH` | [`0x4cecf1…f3a6e`](https://explorer-studio.genlayer.com/tx/0x4cecf1535f10e008244ac9f3f5a1fe3dac18e07b70ab81a3a39b1bcf4a9f3a6e) |
| Register campaign | recall `0` | [`0x6eb030…5bd43`](https://explorer-studio.genlayer.com/tx/0x6eb03095417e3f3667579b40b5698fee1758612ee78f820d7d502cf1cfc5bd43) |
| Outsider activation rejected | `CREATOR_ONLY` | [`0x90265d…ba399`](https://explorer-studio.genlayer.com/tx/0x90265d6bd7ceef33948407df2ad16a53ef339eedd1b40e70ee56383de32ba399) |
| Publisher activates authenticated campaign | `RECALL_ACTIVATED` | [`0x11e626…4a257`](https://explorer-studio.genlayer.com/tx/0x11e6265b2f43f770f23e506501a66e9fdc7061c4b400d460f87e4e85f1f4a257) |
| Independent screener: matching batch | screen `0`, `AFFECTED` | [`0xf8c38d…7ad52`](https://explorer-studio.genlayer.com/tx/0xf8c38ddccb0c1aba971d3b5f3b43df55b7eaa5498a20b8f351440276d157ad52) |
| Publisher: outside-lot batch | screen `1`, `NOT_AFFECTED` | [`0xcd4100…cd8b7b`](https://explorer-studio.genlayer.com/tx/0xcd41002840ff4bb0f770bd76427fd7a1aca1c12ee4636cf8e544d18cd0cd8b7b) |
| Duplicate batch digest | `DUPLICATE_SCREEN`, counts remain `1|2` | [`0xa973a5…79d03`](https://explorer-studio.genlayer.com/tx/0xa973a5de6acd2e3b65cd7089c179c0ff8c696b6a0f99612cc43893db05f79d03) |

Every row reached `FINALIZED`, returned the expected value, and passed authoritative `get_counts`, `get_recall`, and `get_screen` readback. The sanitized JSON evidence excludes private keys and full receipts.
