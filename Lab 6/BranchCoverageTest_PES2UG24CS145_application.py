"""Test cases written to take both outcomes of every decision in atm_withdrawal.py.

Includes the code coverage cases, plus the branch and boundary cases they miss.

Run:
    coverage run --branch -m pytest BranchCoverageTest_PES2UG24CS145_application.py
    coverage report -m
"""
import pytest
from atm_withdrawal import withdraw, pin_check, note_breakup


# ---------- withdraw: account type ----------

def test_simple_withdrawal():
    assert withdraw(5000, 1000, "savings", True) == 4000


def test_unknown_account_type_raises():
    with pytest.raises(ValueError, match="unknown account"):
        withdraw(5000, 1000, "salary", True)


# ---------- withdraw: amount validation ----------

def test_zero_amount_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        withdraw(5000, 0, "savings", True)


def test_negative_amount_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        withdraw(5000, -100, "savings", True)


def test_amount_not_multiple_of_100_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        withdraw(5000, 150, "savings", True)


# ---------- withdraw: daily limit ----------

def test_amount_over_savings_limit():
    assert withdraw(100000, 25100, "savings", True) == "limit exceeded"


def test_amount_at_savings_limit_is_allowed():
    assert withdraw(100000, 25000, "savings", True) == 75000


def test_amount_over_current_limit():
    assert withdraw(100000, 50100, "current", True) == "limit exceeded"


def test_amount_at_current_limit_is_allowed():
    assert withdraw(100000, 50000, "current", True) == 50000


# ---------- withdraw: fees ----------

def test_own_bank_large_amount_pays_no_fee():
    assert withdraw(50000, 20000, "current", True) == 30000


def test_other_bank_large_amount_pays_higher_fee():
    # Other bank, above 10000: fee is 20 + 10 = 30.
    assert withdraw(50000, 20000, "current", False) == 29970


def test_other_bank_small_amount_pays_base_fee():
    # Branch 14->16: other bank, 10000 or less, so the extra 10 is skipped.
    assert withdraw(5000, 1000, "savings", False) == 3980


def test_other_bank_fee_boundary_at_10000():
    assert withdraw(20000, 10000, "savings", False) == 9980


def test_other_bank_fee_boundary_above_10000():
    assert withdraw(20000, 10100, "savings", False) == 9870


# ---------- withdraw: balance check ----------

def test_insufficient_funds():
    assert withdraw(500, 1000, "savings", True) == "insufficient funds"


def test_balance_exactly_covers_amount():
    assert withdraw(1000, 1000, "savings", True) == 0


def test_balance_exactly_covers_amount_and_fee():
    assert withdraw(1020, 1000, "savings", False) == 0


def test_balance_covers_amount_but_not_fee():
    assert withdraw(1019, 1000, "savings", False) == "insufficient funds"


# ---------- pin_check ----------

def test_correct_pin():
    assert pin_check(1234, 1234, 0) == "ok"


def test_correct_pin_on_last_attempt():
    assert pin_check(1234, 1234, 2) == "ok"


def test_card_already_blocked():
    assert pin_check(1234, 1234, 3) == "card blocked"


def test_card_blocked_beyond_three_attempts():
    assert pin_check(1111, 1234, 5) == "card blocked"


def test_wrong_pin_on_last_attempt_blocks_card():
    assert pin_check(1111, 1234, 2) == "card blocked"


def test_wrong_pin_can_retry():
    assert pin_check(1111, 1234, 0) == "retry"


def test_wrong_pin_on_second_attempt_can_retry():
    assert pin_check(1111, 1234, 1) == "retry"


# ---------- note_breakup ----------

def test_note_breakup_invalid_amount_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        note_breakup(150)


def test_note_breakup_uses_200_notes():
    assert note_breakup(900) == (1, 2, 0)


def test_note_breakup_without_200_notes():
    assert note_breakup(600) == (1, 0, 1)


def test_note_breakup_exact_500_notes():
    assert note_breakup(1000) == (2, 0, 0)


def test_note_breakup_remainder_at_200_boundary():
    assert note_breakup(200) == (0, 1, 0)


def test_note_breakup_uses_all_denominations():
    assert note_breakup(800) == (1, 1, 1)


def test_note_breakup_zero():
    assert note_breakup(0) == (0, 0, 0)
