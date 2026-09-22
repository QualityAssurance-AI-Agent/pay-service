"""Tests for the payments read API.

These are the tests the release agent discovers and runs. They are real: they
fail if the response shape or the rounding changes, which is the point — a gate
that cannot fail protects nothing.
"""

from __future__ import annotations

import pytest

from api import PaymentNotFound, get_payment, search_payments
from validation import ValidationError, validate_amount, validate_currency


class Store:
    ROWS = [
        {"id": "pay_1001", "amount_minor": 1299, "currency": "USD",
         "status": "settled", "created_at": "2026-09-01T10:00:00Z",
         "settled_at": "2026-09-01T10:00:04Z"},
        {"id": "pay_1002", "amount_minor": 45050, "currency": "USD",
         "status": "pending", "created_at": "2026-09-02T11:30:00Z"},
    ]

    def search(self, query, limit):
        return [r for r in self.ROWS if query.lower() in r["id"].lower()][:limit]

    def get(self, payment_id):
        return next((r for r in self.ROWS if r["id"] == payment_id), None)


def test_search_reports_the_query_it_applied():
    """An empty result and a dropped filter must be distinguishable."""
    body = search_payments(Store(), query="pay_1001")
    assert body["query"] == "pay_1001"
    assert body["count"] == 1
    assert body["payments"][0]["id"] == "pay_1001"


def test_amount_display_rounds_to_two_places():
    body = search_payments(Store(), query="pay_1002")
    assert body["payments"][0]["amount_display"] == "450.50 USD"


def test_limit_outside_the_allowed_range_is_refused():
    with pytest.raises(ValueError):
        search_payments(Store(), query="pay", limit=0)
    with pytest.raises(ValueError):
        search_payments(Store(), query="pay", limit=101)


def test_single_payment_carries_the_settlement_timestamps():
    view = get_payment(Store(), "pay_1001")
    assert view["created_at"] == "2026-09-01T10:00:00Z"
    assert view["settled_at"] == "2026-09-01T10:00:04Z"


def test_settlement_is_reported_explicitly_not_inferred():
    """Absence of a timestamp is not the same as not having settled."""
    assert get_payment(Store(), "pay_1001")["is_settled"] is True
    assert get_payment(Store(), "pay_1002")["is_settled"] is False


def test_a_pending_payment_has_no_settled_at():
    assert get_payment(Store(), "pay_1002")["settled_at"] is None


def test_an_unknown_payment_is_not_found():
    with pytest.raises(PaymentNotFound):
        get_payment(Store(), "pay_9999")


def test_an_amount_must_be_a_positive_integer_of_minor_units():
    with pytest.raises(ValidationError):
        validate_amount(0)
    with pytest.raises(ValidationError):
        validate_amount(-1)
    with pytest.raises(ValidationError):
        validate_amount(12.99)          # a float is a rounding bug waiting to happen
    validate_amount(1299)               # and this one is fine


def test_an_amount_over_the_per_payment_limit_is_refused():
    with pytest.raises(ValidationError):
        validate_amount(100_000_01)


def test_an_unsupported_currency_is_refused_and_says_what_is_supported():
    with pytest.raises(ValidationError) as caught:
        validate_currency("XYZ")
    assert "USD" in str(caught.value)
    validate_currency("USD")
