# pay-service

The payments read API, and the console that searches it.

    services/pay/   the API: search payments, fetch one          (Python 3.12, Lambda)
    web/            the search console                           (React, TypeScript)
    docs/           what support and on-call read

## Running the tests

```bash
cd services/pay && pytest tests      # the API
cd web && npm test                   # the console
```

Amounts are stored and passed around in minor units, as integers. The tests pin the
rounding, so changing how an amount is formatted will fail them — which is the point.

## Releasing

How this service is released is written down in [`AGENTS.md`](AGENTS.md), under
**Release rules**, in prose. There is nothing else: no pipeline definition, no list of
which tests gate which environment. Those are the rules, and they are meant to be read
by people first.
