"""
A tiny stand-in for a real payment gateway (Stripe / JazzCash / Easypaisa).

It follows the same test-card convention so the checkout code path is the same one you would
write against a real provider: the service asks the gateway to charge, and reacts to
success or a decline. Swapping in a real provider later only means replacing `charge()`.

Test cards
  4242 4242 4242 4242  -> succeeds
  4000 0000 0000 0002  -> declined
  4000 0000 0000 9995  -> insufficient funds
Any other Luhn-valid number succeeds; anything else is rejected as invalid.
"""
import re
import uuid
from dataclasses import dataclass

DECLINES = {
    "4000000000000002": "Your card was declined.",
    "4000000000009995": "Your card has insufficient funds.",
}


@dataclass
class GatewayResult:
    success: bool
    reference: str = ""
    message: str = ""
    last4: str = ""


def _luhn_ok(number: str) -> bool:
    total, alt = 0, False
    for ch in reversed(number):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def charge(card_number: str, amount) -> GatewayResult:
    digits = re.sub(r"\D", "", card_number or "")
    if not 13 <= len(digits) <= 19 or not _luhn_ok(digits):
        return GatewayResult(False, message="That card number is not valid.")
    if digits in DECLINES:
        return GatewayResult(False, message=DECLINES[digits], last4=digits[-4:])
    return GatewayResult(True, reference=f"ch_{uuid.uuid4().hex[:14]}", last4=digits[-4:])
