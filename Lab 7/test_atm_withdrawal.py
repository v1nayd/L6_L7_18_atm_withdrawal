"""Lab 7 - Fuzz tests (Hypothesis) for atm_withdrawal.py

Three layers of properties are checked for every function:
  1. "Never crash"  - whatever garbage is passed in (text, None, ints, floats,
                      bytes, lists ...) the function must not raise.
  2. "Correct output" - for well-formed inputs the answer must be right.
  3. "Reject bad input" - for malformed inputs the function must signal it
                      safely (return None) instead of guessing or leaking data.
"""
import re

from hypothesis import given, settings, example, strategies as st

from atm_withdrawal import notes_needed, mask_card, average_withdrawal

settings.register_profile("lab7", max_examples=300, deadline=None)
settings.load_profile("lab7")

# Anything a caller (or a malicious user) could possibly hand to a function.
anything = st.one_of(
    st.none(),
    st.text(),
    st.integers(),
    st.floats(allow_nan=True, allow_infinity=True),
    st.binary(),
    st.booleans(),
    st.lists(st.integers()),
)


# ---------------------------------------------------------------------------
# 1. notes_needed
# ---------------------------------------------------------------------------
@given(st.text() | st.none())
@example("abc")        # ValueError in the buggy version
@example("")           # ValueError
@example(None)         # AttributeError
@example(",")          # ValueError after removing the comma
@example("-500")       # negative amount
def test_notes_needed_no_crash(s):
    try:
        notes_needed(s)
    except Exception as e:
        assert False, f"notes_needed crashed with: {e!r} for input {s!r}"


@given(anything)
def test_notes_needed_never_crashes_on_any_type(x):
    try:
        notes_needed(x)
    except Exception as e:
        assert False, f"notes_needed crashed with: {e!r} for input {x!r}"


@given(st.integers(min_value=0, max_value=10 ** 9))
def test_notes_needed_correct_for_valid_amounts(n):
    # "2,500" style (thousands separators) and plain "2500" must both work
    assert notes_needed(f"{n:,}") == n // 100
    assert notes_needed(str(n)) == n // 100


@given(st.text() | st.none())
def test_notes_needed_result_is_none_or_non_negative_int(s):
    result = notes_needed(s)
    assert result is None or (isinstance(result, int) and result >= 0)


@given(st.integers(min_value=1, max_value=10 ** 9))
def test_notes_needed_rejects_negative_amounts(n):
    assert notes_needed(f"-{n}") is None


# ---------------------------------------------------------------------------
# 2. mask_card
# ---------------------------------------------------------------------------
@given(st.text() | st.none())
@example("1234 5678")   # IndexError in the buggy version
@example("")            # IndexError
@example(None)          # AttributeError
@example("a b c d")     # buggy version echoes arbitrary text back
def test_mask_card_no_crash(s):
    try:
        mask_card(s)
    except Exception as e:
        assert False, f"mask_card crashed with: {e!r} for input {s!r}"


@given(anything)
def test_mask_card_never_crashes_on_any_type(x):
    try:
        mask_card(x)
    except Exception as e:
        assert False, f"mask_card crashed with: {e!r} for input {x!r}"


@given(st.text(alphabet="0123456789", min_size=16, max_size=16))
def test_mask_card_masks_all_but_last_four_digits(digits):
    grouped = " ".join(digits[i:i + 4] for i in range(0, 16, 4))
    result = mask_card(grouped)
    assert result == "XXXX XXXX XXXX " + digits[-4:]
    # nothing except the last four digits may ever leak into the output
    assert re.findall(r"\d", result) == list(digits[-4:])


@given(st.text() | st.none())
def test_mask_card_never_leaks_more_than_last_four_digits(s):
    result = mask_card(s)
    if result is not None:
        assert isinstance(result, str)
        assert result.startswith("XXXX XXXX XXXX ")
        assert re.fullmatch(r"XXXX XXXX XXXX [0-9]{4}", result)


@given(st.text(alphabet="0123456789", min_size=0, max_size=15))
def test_mask_card_rejects_too_short_numbers(digits):
    assert mask_card(digits) is None


# ---------------------------------------------------------------------------
# 3. average_withdrawal
# ---------------------------------------------------------------------------
@given(st.text() | st.none())
@example("")            # ValueError / would be ZeroDivisionError if empty list
@example(",")           # ValueError (empty elements)
@example("1,,3")       # empty element
@example("one,two")    # non-numeric
@example(None)          # AttributeError
def test_average_withdrawal_no_crash(s):
    try:
        average_withdrawal(s)
    except Exception as e:
        assert False, f"average_withdrawal crashed with: {e!r} for input {s!r}"


@given(anything)
def test_average_withdrawal_never_crashes_on_any_type(x):
    try:
        average_withdrawal(x)
    except Exception as e:
        assert False, f"average_withdrawal crashed with: {e!r} for input {x!r}"


@given(st.lists(st.integers(min_value=0, max_value=10 ** 7), min_size=1, max_size=50))
def test_average_withdrawal_correct_for_valid_lists(nums):
    result = average_withdrawal(",".join(str(n) for n in nums))
    assert result == sum(nums) // len(nums)
    assert min(nums) <= result <= max(nums)


@given(st.lists(st.integers(min_value=0, max_value=10 ** 7), min_size=1, max_size=20))
def test_average_withdrawal_ignores_spaces_around_values(nums):
    assert average_withdrawal(" , ".join(str(n) for n in nums)) == sum(nums) // len(nums)


@given(st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=10),
       st.integers(min_value=1, max_value=1000))
def test_average_withdrawal_rejects_negative_values(nums, bad):
    assert average_withdrawal(",".join(map(str, nums + [-bad]))) is None


@given(st.text() | st.none())
def test_average_withdrawal_result_is_none_or_non_negative_int(s):
    result = average_withdrawal(s)
    assert result is None or (isinstance(result, int) and result >= 0)
