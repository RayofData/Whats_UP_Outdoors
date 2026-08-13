import pytest

from src.locations import normalize_zipcode


@pytest.mark.parametrize(
    "zipcode, expected",
    [
        ("49781", "49781"),
        (" 49781 ", "49781"),
        ("48657", "48657"),
        ("77871", "77871"),
    ],
)
def test_normalize_zipcode_accepts_valid_format(zipcode, expected):
    """Valid five-digit ZIP codes should be normalized and returned."""
    result = normalize_zipcode(zipcode)

    assert result == expected


@pytest.mark.parametrize(
    "invalid_zipcode",
    [
        "abc",
        "ABCDE",
        "4978",
        "497811",
    ],
)
def test_normalize_zipcode_rejects_invalid_format(invalid_zipcode):
    """ZIP codes that are not exactly five digits should raise ValueError."""
    with pytest.raises(ValueError):
        normalize_zipcode(invalid_zipcode)