# PlateSignal

PlateSignal is an evidence-bound menu claim cross-check built on GenLayer. It compares one exact dish and allergen across a public menu and an independently hosted allergen guide, then preserves the source receipts and exact quotes behind the result.

It is not a food-safety guarantee or medical advice. A conflict produces a deliberately cautious `AVOID_UNTIL_CONFIRMED` action; users should verify with qualified restaurant staff.

## Why decentralized judgment matters

Menu and allergen language is messy: “dairy-free,” “may contain,” “prepared in a shared facility,” and ingredient disclosures can conflict without sharing a schema. A normal smart contract cannot interpret those natural-language differences. PlateSignal lets GenLayer validators independently judge the exact frozen evidence while deterministic contract code verifies URLs, source attribution, output shape, quote membership, permissions, correction limits, and final state.

## Lifecycle

1. `open_report` stores an exact restaurant, dish, allergen, advertised claim, and two different HTTPS hosts.
2. `review_report` retrieves both pages under strict equality and asks independent validators to classify the menu and guide.
3. The report owner may call `attach_correction` once during a 12-hour window using a third host. The previous finding remains in history.
4. `seal_report` creates a deterministic final receipt. The owner can seal early; anyone can seal after the correction window.

## Consensus boundaries

- source bodies are retrieved before judgment and frozen with `strict_eq`;
- the non-comparative callback returns deterministic JSON input only;
- validators receive an explicit task and equivalence criteria;
- prompt text inside fetched pages is treated as untrusted content;
- every quote is checked against its cited frozen source;
- a `CONFLICT` requires evidence from at least two source indexes;
- unavailable sources cannot produce a substantive safety claim;
- menu and guide hosts must differ, and a correction must use a third host.

## Findings

- `CONFLICT`: the exact menu claim materially clashes with the guide;
- `ALIGNED`: both readable sources explicitly agree;
- `INSUFFICIENT`: the exact dish/allergen binding is too weak;
- `SOURCE_UNAVAILABLE`: at least one required source could not be retrieved.

## Run locally

```bash
npm install
npm --prefix frontend install
npm test
npm run frontend:test
npm run build
npm --prefix frontend run dev
```

Copy `frontend/.env.example` to `frontend/.env` and set the deployed contract address.

## Test coverage

The direct contract suite covers duplicate IDs, URL and host boundaries, persisted review state, replay rejection, owner-only correction, third-host enforcement, immutable history, expiration, early-owner sealing, permissionless sealing, and multiple exact quotes per source. Frontend tests cover serialization, finding states, owner/time correction permissions, and compact formatting.

## Demo fixture disclosure

Files in `frontend/public/demo/` are synthetic test fixtures and are labeled as such. They prove the live consensus path without implying a real restaurant or real allergen notice.

