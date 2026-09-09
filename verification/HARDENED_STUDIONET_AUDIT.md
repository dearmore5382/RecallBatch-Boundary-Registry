# Hardened Studionet audit

- Current contract: [`0x1E09EDDbd1dde3eC95f150D02304f542d511132F`](https://explorer-studio.genlayer.com/address/0x1E09EDDbd1dde3eC95f150D02304f542d511132F)
- Exact deployed/local SHA-256: `48ae82af9846e4e9fcfed307483bfab4ee448da0a9e5dda2cf01087aedfc5378`
- Fixture commit: [`a7a2a800`](https://github.com/dearmore5382/RecallBatch-Boundary-Registry/tree/a7a2a800a45553fed12ab75b9affd46ed79c0f11/test-fixtures)
- Final state: recall `0` superseded by recall `1`; recall `1` active; two immutable screens.

## Owner trust bootstrap

| Action | FINALIZED transaction |
|---|---|
| Owner grants publisher role to `0x736A…9c8bB` | [`0xd64b21…5340c`](https://explorer-studio.genlayer.com/tx/0xd64b21bed0f6f4e72e93a764a3e92fd9a674fdff380ab43f2f8ff45fad35340c) |
| Owner grants attestor role to `0xA63D…6eDBE` | [`0xb7004c…2a685`](https://explorer-studio.genlayer.com/tx/0xb7004c682a0a8b43d77fa0f96f730db00831549159a967557cc58106e9e2a685) |

## Checkpointed adversarial matrix

| Case | Expected and actual | FINALIZED transaction |
|---|---|---|
| Untrusted recall publication | `PUBLISHER_ONLY` | [`0x8bf985…0f137`](https://explorer-studio.genlayer.com/tx/0x8bf985d0b5283ea611db2a3d9b26b96a32dc3f6541c7626faecc36023c10f137) |
| Untrusted batch screening | `ATTESTOR_ONLY` | [`0x9618c5…68049`](https://explorer-studio.genlayer.com/tx/0x9618c5cf9d4f6d0aaa64a3e787e6f8386056f4fcec18b5ac4813a2fbc8e68049) |
| Non-owner grant attempt | `OWNER_ONLY` | [`0x02cd92…97992`](https://explorer-studio.genlayer.com/tx/0x02cd927d56a75fc17860730d5d5f13a08a144f3ac21db1455777218c19d97992) |
| Attestor self-promotion attempt | `OWNER_ONLY` | [`0xfdbea6…eaf25`](https://explorer-studio.genlayer.com/tx/0xfdbea6efa172f0e19bc6f173464957c64a17f571cb11215201ba6468673eaf25) |
| Authorized campaign registration | recall `0` | [`0x66d21a…7af9d`](https://explorer-studio.genlayer.com/tx/0x66d21ab4154ec7b1b1848ef440507a7432ed9714d1b4d85be2aacb70fe47af9d) |
| Wrong publisher activation | `PUBLISHER_ONLY` | [`0x717d7c…1e99f`](https://explorer-studio.genlayer.com/tx/0x717d7c6a9f3b9e019cabde9fd7c489b27d67ba98c14a5c0fd6d6f74b8d11e99f) |
| Publisher activates authenticated source | `RECALL_ACTIVATED` | [`0x3b7d98…d2e65`](https://explorer-studio.genlayer.com/tx/0x3b7d9832fef7ef5879066cdb5cd5cce2c4f99dc601e4523a386878749acd2e65) |
| Issuer-bound matching batch | screen `0`, `AFFECTED` | [`0xd3e12a…a9284`](https://explorer-studio.genlayer.com/tx/0xd3e12a06cf8d60ea62de30fa3f332d4b829683104cb021f34a78ee989dea9284) |
| Issuer-bound outside-lot batch | screen `1`, `NOT_AFFECTED` | [`0xd0d7d0…b1b1f`](https://explorer-studio.genlayer.com/tx/0xd0d7d002d632b2cdb3b4f1ba277a69a48d12b9e0c51afa0b622804061a8b1b1f) |
| Different bytes/reference, same canonical lot | `DUPLICATE_SCREEN`, counts remain `1|2` | [`0xd86c98…b9570`](https://explorer-studio.genlayer.com/tx/0xd86c98f5b501a0132dd4cc16ac7247f6bbcb784f2903307bf574f3dbf7eb9570) |
| Register replacement | recall `1` | [`0xc140ce…19ac5`](https://explorer-studio.genlayer.com/tx/0xc140cea2c216fbbf1f4b0c612ce3f196941b9d806fe8ea4415e6c1d3f0219ac5) |
| Activate replacement | `RECALL_ACTIVATED` | [`0xe8eb1b…a4ffc`](https://explorer-studio.genlayer.com/tx/0xe8eb1ba0232c7439280e6c43266fbc32de07d63fe4d21b4a74a1ad45650a4ffc) |
| Supersede original with replacement | `RECALL_SUPERSEDED` | [`0x4b1129…e5845`](https://explorer-studio.genlayer.com/tx/0x4b11290878c01916bcf40a35690c0e2469f9cb8801153c670f895b04c6be5845) |
| Screen against superseded campaign | `RECALL_NOT_ACTIVE`, counts remain `2|2` | [`0xeae11a…658e5`](https://explorer-studio.genlayer.com/tx/0xeae11a7e80d0c4f878bc72a28fd2d2906ec5cc7741fbda5e425a4c55f9a658e5) |

All matrix transactions are FINALIZED, consensus accepted, return values matched expectations, and authoritative state readback passed. No private keys or full validator receipts are published.
