"""AWS Lambda entry point for the payments read API.

The response deliberately reports which commit was packaged. A release that
claims success is easy to fake; a running function that names the change it came
from is not. This is what makes "the thing deployed is the thing that was built"
checkable from outside the pipeline, with nothing but an invoke.
"""

from __future__ import annotations

import json
import pathlib

from api import PaymentNotFound, get_payment, search_payments

#: Written into the package by the build step. Absent when someone runs the
#: handler straight out of a source tree, which is worth distinguishing from a
#: build that failed to record itself.
_BUILD_INFO = pathlib.Path(__file__).with_name("BUILD_INFO.json")


def build_info() -> dict:
    """What the build recorded about this package."""
    if not _BUILD_INFO.exists():
        return {"commit": "unpackaged", "built_at": "unpackaged"}
    return json.loads(_BUILD_INFO.read_text())


class _Store:
    """A stand-in for the payments datastore, so the handler exercises real code.

    The point of invoking this function in a release is to prove the packaged
    business logic runs, so the handler calls the same code paths the service
    uses rather than returning a constant.
    """

    _ROWS = [
        {"id": "pay_1001", "amount_minor": 1299, "currency": "USD",
         "status": "settled", "created_at": "2026-09-01T10:00:00Z",
         "settled_at": "2026-09-01T10:00:04Z"},
        {"id": "pay_1002", "amount_minor": 45050, "currency": "USD",
         "status": "pending", "created_at": "2026-09-02T11:30:00Z"},
    ]

    def search(self, query: str, limit: int):
        hits = [r for r in self._ROWS if query.lower() in r["id"].lower()]
        return hits[:limit]

    def get(self, payment_id: str):
        for row in self._ROWS:
            if row["id"] == payment_id:
                return row
        return None


def lambda_handler(event, context):  # noqa: ARG001 - Lambda passes both
    """Answer a read request, and say which build answered it."""
    store = _Store()
    payment_id = (event or {}).get("payment_id")

    if payment_id:
        try:
            body = get_payment(store, payment_id)
        except PaymentNotFound:
            return {"service": "pay-api", "build": build_info(),
                    "error": f"no payment {payment_id}"}
    else:
        body = search_payments(store, query=(event or {}).get("query", "pay"))

    return {"service": "pay-api", "build": build_info(), "result": body}
