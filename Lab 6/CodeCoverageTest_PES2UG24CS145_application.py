"""Test cases written to execute every line of atm_withdrawal.py.

Run:
    coverage run -m pytest CodeCoverageTest_PES2UG24CS145_application.py
    coverage report -m
"""
import pytest
from atm_withdrawal import withdraw, pin_check, note_breakup


# ---------- withdraw ----------

def test_simple_withdrawal():
    assert withdraw(5000, 1000, "savings", True) == 4000


def test_unknown_account_type_raises():
    with pytest.raises(ValueError, match="unknown account"):
        withdraw(5000, 1000, "salary", True)


def test_zero_amount_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        withdraw(5000, 0, "savings", True)


def test_amount_over_daily_limit():
    assert withdraw(100000, 25100, "savings", True) == "limit exceeded"


def test_other_bank_large_amount_pays_higher_fee():
    # Other bank, above 10000: fee is 20 + 10 = 30.
    assert withdraw(50000, 20000, "current", False) == 29970


def test_insufficient_funds():
    assert withdraw(500, 1000, "savings", True) == "insufficient funds"


# ---------- pin_check ----------

def test_correct_pin():
    assert pin_check(1234, 1234, 0) == "ok"


def test_card_already_blocked():
    assert pin_check(1234, 1234, 3) == "card blocked"


def test_wrong_pin_on_last_attempt_blocks_card():
    assert pin_check(1111, 1234, 2) == "card blocked"


def test_wrong_pin_can_retry():
    assert pin_check(1111, 1234, 0) == "retry"


# ---------- note_breakup ----------

def test_note_breakup_invalid_amount_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        note_breakup(150)


def test_note_breakup_uses_200_notes():
    assert note_breakup(900) == (1, 2, 0)


def test_note_breakup_without_200_notes():
    assert note_breakup(600) == (1, 0, 1)
