import pytest
from shapely.geometry import Point 

from src.locations import normalize_zipcode, zip_to_point, get_zip_info



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


@pytest.mark.parametrize(
    "valid_zipcode",
    [
        "49781",
        " 49781 ",
        "48657",
        "77871",
    ],
)
def test_zip_to_point_returns_point(valid_zipcode):
    """A resolvable ZIP code should return a Shapely Point."""
    result = zip_to_point(valid_zipcode)

    assert isinstance(result, Point)

@pytest.mark.parametrize(
    "invalid_zipcode",
    [
        "00000",
        "99999",
        "00500"
    ],
)
def test_zip_to_point_rejects_invalid_zip(invalid_zipcode):
    """ZIP codes that are not valid US ZIP codes should raise ValueError."""
    with pytest.raises(ValueError):
        zip_to_point(invalid_zipcode)

def test_zip_to_point_coordinates_in_global_range():
    """A correct ZIP point should contain valid longitude and latitude."""
    point = zip_to_point("49781")
    assert -180 <= point.x <= 180
    assert -90 <= point.y <= 90


@pytest.mark.parametrize(
    "valid_zipcode",
    [
        "49781",
        " 49781 ",
        "48657",
        "77871",
    ],
)
def test_get_zip_info_returns_info(valid_zipcode):
    """Verify get zip info returns the correct keys."""
    result = get_zip_info(valid_zipcode)

    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "zipcode",
        "place",
        "county",
        "state",
    }

@pytest.mark.parametrize(
    "invalid_zipcode",
    [
        "00000",
        "99999",
        "00500"
    ],
)
def test_get_zip_info_rejects_invalid_zip(invalid_zipcode):
    """An invalid five-digit U.S. ZIP codes should raise ValueError."""
    with pytest.raises(ValueError):
        get_zip_info(invalid_zipcode)

def test_get_zip_info_returns_expected_up_location():
    """ZIP 49781 should resolve to the expected Upper Peninsula location."""
    result = get_zip_info("49781")

    assert result["zipcode"] == "49781"
    assert result["county"] == "Mackinac"
    assert result["state"] == "Michigan"
    assert result["place"] == "Saint Ignace"
    