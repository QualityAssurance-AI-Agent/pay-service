# Payments API

## GET /api/payments

Query parameters: `q` (required), `limit` (optional, 1..100, default 25).

Response body:

    { "query": "...", "payments": [ { "id", "amount_minor", "currency", "status" } ] }

## Currencies

USD, EUR, GBP, JPY, CHF and SEK are accepted. Others are rejected with the
supported list in the error message.

## Limits

A single payment may not exceed 100,000 in its currency.
