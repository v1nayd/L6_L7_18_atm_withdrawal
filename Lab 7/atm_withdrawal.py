"""ATM withdrawal helpers (Lab 7 - hardened after fuzz testing).

Every public function validates its input and returns ``None`` when the input
is invalid instead of raising an exception, so a bad value typed by a user (or
produced by a fuzzer) can never crash the ATM.
"""
import re

NOTE_VALUE = 100          # denomination of the notes dispensed
MAX_DIGITS = 12           # longest amount accepted (blocks huge-number DoS)
MAX_ITEMS = 10_000        # most CSV entries accepted (blocks giant-input DoS)
CARD_DIGITS = 16          # card numbers must have exactly 16 digits

# ASCII digits only: str.isdigit()/\d also match characters like '²' or '٣'
# which int() may reject or interpret differently.
_AMOUNT_RE = re.compile(r"[0-9]+(,[0-9]+)*")
_DIGITS_RE = re.compile(r"[0-9]+")


def _parse_amount(text):
    """Return a non-negative int for a clean amount string, else None."""
    if not isinstance(text, str):
        return None
    if _DIGITS_RE.fullmatch(text) is None:
        return None
    if len(text) > MAX_DIGITS:
        return None
    return int(text)


def notes_needed(amount):
    """Number of 100-notes for an amount such as '2,500' or '2500'.

    Returns None for anything that is not a non-negative whole number.
    """
    if not isinstance(amount, str):
        return None
    amount = amount.strip()
    if _AMOUNT_RE.fullmatch(amount) is None:
        return None
    value = _parse_amount(amount.replace(",", ""))
    if value is None:
        return None
    return value // NOTE_VALUE


def mask_card(card_number):
    """Mask a 16-digit card number, keeping only the last four digits.

    Accepts spaces or hyphens between digit groups. Returns None if the input
    is not exactly 16 digits (nothing from invalid input is echoed back).
    """
    if not isinstance(card_number, str):
        return None
    digits = re.sub(r"[ \-]", "", card_number.strip())
    if _DIGITS_RE.fullmatch(digits) is None or len(digits) != CARD_DIGITS:
        return None
    return "XXXX XXXX XXXX " + digits[-4:]


def average_withdrawal(amounts_csv):
    """Integer average of comma-separated withdrawals such as '500,1000,2000'.

    Returns None for empty input, empty/non-numeric/negative entries, or
    absurdly long input.
    """
    if not isinstance(amounts_csv, str):
        return None
    parts = amounts_csv.split(",")
    if len(parts) > MAX_ITEMS:
        return None
    amounts = []
    for part in parts:
        value = _parse_amount(part.strip())
        if value is None:
            return None
        amounts.append(value)
    return sum(amounts) // len(amounts)


def main():
    try:
        print("==== Running notes_needed ====")
        user_input = input("Enter an amount (e.g. 2,500): ")
        result = notes_needed(user_input)
        if result is None:
            print("Invalid amount: enter a whole number such as 2,500")
        else:
            print("Number of 100 Notes:", result)

        print("\n==== Running mask_card ====")
        user_input = input("Enter a card number (e.g. 1234 5678 9012 3456): ")
        result = mask_card(user_input)
        if result is None:
            print("Invalid card number: enter 16 digits such as 1234 5678 9012 3456")
        else:
            print("Masked Card:", result)

        print("\n==== Running average_withdrawal ====")
        user_input = input("Enter withdrawals as CSV (e.g. 500,1000,2000): ")
        result = average_withdrawal(user_input)
        if result is None:
            print("Invalid withdrawals: enter whole numbers separated by commas")
        else:
            print("Average Withdrawal:", result)
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")


if __name__ == "__main__":
    main()
