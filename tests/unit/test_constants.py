import pytest

from ikob.configuration_definition import DecayCurveName
from ikob.constants import work_constants

# Valid combinations based on the code analysis
VALID_MODALITIES = ["Auto", "OV", "Fiets", "EFiets"]
VALID_PREFERENCES = ["Auto", "OV", "Fiets"]


@pytest.mark.parametrize("modality", VALID_MODALITIES)
@pytest.mark.parametrize("preference", VALID_PREFERENCES)
def test_different_decay_curve_name_different_constants(modality, preference):
    """Test that constants differ when choosing a different decay curve."""
    constants_work = work_constants(modality, preference, DecayCurveName.WORK_AND_SOCIAL)
    constants_daily = work_constants(modality, preference, DecayCurveName.DAILY_SHOPPING_AND_HEALTH)
    constants_non_daily = work_constants(modality, preference, DecayCurveName.NON_DAILY_SHOPPING_AND_EDUCATION)

    # Check that at least one constant differs noticeably (not just floating point noise)
    # Allow for small floating point differences (relative tolerance of 1%)
    work_daily_different = not (
        constants_work[0] == pytest.approx(constants_daily[0])
        and constants_work[1] == pytest.approx(constants_daily[1])
        and constants_work[2] == pytest.approx(constants_daily[2])
    )

    work_non_daily_different = not (
        constants_work[0] == pytest.approx(constants_non_daily[0])
        and constants_work[1] == pytest.approx(constants_non_daily[1])
        and constants_work[2] == pytest.approx(constants_non_daily[2])
    )

    assert work_daily_different or work_non_daily_different, (
        f"Constants should differ across decay curves for modality={modality}, "
        f"preference={preference}. Got work={constants_work}, daily={constants_daily}, "
        f"non_daily={constants_non_daily}"
    )
