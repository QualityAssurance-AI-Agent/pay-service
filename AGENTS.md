# Working on the payments service

A small read API over payments: search and fetch one.

Amounts are stored and passed around in **minor units** (cents), as integers. Nothing
here should hold money in a float. Formatting to a human-readable string happens once,
in `_view`, and the tests pin the rounding — if you change it you will see them fail,
which is the point.

```
services/pay/        api.py, handler.py, validation.py
services/pay/tests/  pytest, run with `pytest tests` from services/pay
web/                 the search UI
docs/                what support and on-call read
```

`handler.py` is the Lambda entry point. The build stamps `BUILD_INFO.json` into the
package, so a running function can say which commit it came from.

## Release rules

Every deployment must be preceded by a code review that a peer approved, and by a
passing security scan. Nothing reaches an environment without both. The review itself
happens on the pull request; what runs in the release only confirms it was not
skipped.

Any change to source code, services or libraries has to pass unit tests before it is
deployed. Documentation-only changes do not.

Everything under `services/` carries the money path, so any change there must pass a
load test before production. We have been burned by a query that was fine at ten
requests a second and fell over at a hundred.

Production is never the first environment: gamma must be released first. And a
production deployment needs an approval from the on-call SRE — not because we expect
to reject them, but because somebody should know it happened.
