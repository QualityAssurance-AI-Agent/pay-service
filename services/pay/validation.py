"""Request validation for the payments API."""

_CURRENCIES = frozenset({"USD", "EUR", "GBP", "JPY", "CHF", "SEK"})


class ValidationError(ValueError):
    """A request the API refuses to process."""


_MAX_AMOUNT_MINOR = 100_000_00


def validate_amount(amount_minor: int) -> None:
    if not isinstance(amount_minor, int):
        raise ValidationError("amount must be an integer number of minor units")
    if amount_minor <= 0:
        raise ValidationError("amount must be positive")
    if amount_minor > _MAX_AMOUNT_MINOR:
        raise ValidationError(
            f"amount exceeds the per-payment limit of {_MAX_AMOUNT_MINOR // 100}"
        )


def validate_currency(currency: str) -> None:
    if currency not in _CURRENCIES:
        raise ValidationError(
            f"unsupported currency: {currency}; supported: "
            + ", ".join(sorted(_CURRENCIES))
        )
