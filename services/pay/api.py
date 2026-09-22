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
    # Support agents were opening a settled payment and then guessing whether a
    # refund would go through. A payment can be refunded once it has settled and
    # has not been refunded already.
    view["refundable"] = record["status"] == "settled" and not record.get("refunded")
    # Finance was reconciling against the gross amount and reporting a shortfall every
    # month. The processing fee is deducted before settlement, so what a merchant
    # actually receives is the amount less the fee, and both belong in the response.
    view["fee_minor"] = fee_for(record["amount_minor"])
    view["net_minor"] = record["amount_minor"] - view["fee_minor"]
    return view


def fee_for(amount_minor: int) -> int:
    """The processing fee on an amount, in minor units.

    2.9% plus 30 cents, rounded to the nearest minor unit. Rounded once here rather
    than at each caller, which is how the displayed amount came to disagree with the
    settled one.
    """
    return round(amount_minor * 0.029) + 30


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
