"""Module to test datapackage functions."""

from digiplan.map import datapackage


def test_heat_capacity_shares():
    """Test reading heat structure shares from digipipe datapackage."""
    shares = datapackage.get_heat_capacity_shares("dec")
    assert len(shares) == 5
    assert sum(shares.values()) == 1
    # TODO (Hendrik): Central heat structure not yet present
    # https://github.com/rl-institut-private/digiplan/issues/308
