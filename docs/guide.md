# Operating the payments service

## Searching payments

`GET /api/payments?q=<query>` returns up to 25 payments, newest first. Pass
`limit` to change the page size; values outside 1..100 are rejected.

## Environments

Changes are released beta, then gamma, then production. Production requires an
approval from the on-call SRE.

## Support

Ask in #payments-oncall. Include the payment id and the time window you searched.

