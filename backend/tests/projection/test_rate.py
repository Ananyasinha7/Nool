import pytest
from hypothesis import given
from hypothesis import strategies as st

from backend.app.projection.rate import weighted_rate


def test_three_two_one():
    assert weighted_rate([490, 480, 465]) == pytest.approx(482.5)
    assert weighted_rate([290, 310, 305]) == pytest.approx(299.1667, abs=1e-3)


def test_single_log_is_itself():
    assert weighted_rate([400]) == 400


def test_empty_is_zero():
    assert weighted_rate([]) == 0.0


def test_only_three_latest_used():
    assert weighted_rate([300, 300, 300, 9999]) == 300


@given(st.lists(st.integers(0, 5000), min_size=1, max_size=6))
def test_between_min_and_max(xs):
    used = xs[:3]
    assert min(used) - 1e-9 <= weighted_rate(xs) <= max(used) + 1e-9
