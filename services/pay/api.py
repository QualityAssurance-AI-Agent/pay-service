"""Payments read API."""

from dataclasses import dataclass, asdict


@dataclass
class PaymentView:
    """One payment, as returned to the front end."""

    id: str
    amount_minor: int
    currency: str
    status: str
    # New in this change: callers were computing this themselves and getting the
    # rounding wrong, so the API now returns it.
    amount_display: str


class PaymentNotFound(LookupError):
    """No payment with that id."""


def search_payments(store, query: str, limit: int = 25) -> dict:
    """Search payments, newest first.

    Returns the response body: a list of payment views plus the applied query, so
    a caller can tell an empty result from a dropped filter.
    """
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    matches = store.search(query=query, limit=limit)
    return {
        "query": query,
        "count": len(matches),
        "payments": [asdict(_view(record)) for record in matches],
    }


def get_payment(store, payment_id: str) -> dict:
    """Return one payment, with the settlement timestamps callers were asking for."""
    record = store.get(payment_id)
    if record is None:
        raise PaymentNotFound(payment_id)
    view = asdict(_view(record))
    view["created_at"] = record["created_at"]
    view["settled_at"] = record.get("settled_at")
    # Callers were inferring this from settled_at being absent, which broke for
    # payments that settled with no timestamp recorded.
    view["is_settled"] = record["status"] == "settled"
    return view


def _view(record) -> PaymentView:
    minor = record["amount_minor"]
    currency = record["currency"]
    return PaymentView(
        id=record["id"],
        amount_minor=minor,
        currency=currency,
        status=record["status"],
        amount_display=f"{minor / 100:.2f} {currency}",
    )
