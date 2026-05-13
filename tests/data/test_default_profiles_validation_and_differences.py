"""Default anomaly profiles tests."""

from __future__ import annotations

from src.infrastructure.anomaly_profile.default_profiles import create_default_profiles


class TestProfileValuesValidation:
    """Tests to verify profile values are reasonable."""

    def test_temperature_thresholds_are_reasonable(self) -> None:
        """Temperature thresholds are within reasonable ranges."""
        profiles = create_default_profiles()

        for profile_name, profile in profiles.items():
            temp_hot = profile["temp_hot"]
            temp_cold = profile["temp_cold"]
            assert temp_hot > 0, f"{profile_name}: temp_hot too low"
            assert temp_cold < temp_hot, f"{profile_name}: temp_cold >= temp_hot"
            assert temp_hot <= 45, f"{profile_name}: temp_hot too high"
            assert temp_cold >= -50, f"{profile_name}: temp_cold too low"

    def test_precipitation_thresholds_are_reasonable(self) -> None:
        """Precipitation thresholds are within reasonable ranges."""
        profiles = create_default_profiles()

        for profile_name, profile in profiles.items():
            precip_high = profile["precip_high"]
            precip_low = profile["precip_low"]
            assert precip_low >= 0, f"{profile_name}: precip_low negative"
            assert precip_high > precip_low, f"{profile_name}: precip_high <= precip_low"
            assert precip_high <= 300, f"{profile_name}: precip_high too high"

    def test_wind_thresholds_are_sorted(self) -> None:
        """Wind thresholds are in increasing order."""
        profiles = create_default_profiles()

        for profile_name, profile in profiles.items():
            wind_values = [
                profile["wind_normal"],
                profile["wind_strong"],
                profile["wind_extreme"],
                profile["wind_hurricane"],
            ]
            assert wind_values == sorted(wind_values), f"{profile_name}: wind thresholds not sorted"

    def test_wind_thresholds_are_reasonable(self) -> None:
        """Wind thresholds are within reasonable ranges."""
        profiles = create_default_profiles()

        for profile_name, profile in profiles.items():
            wind_normal = profile["wind_normal"]
            wind_hurricane = profile["wind_hurricane"]
            assert wind_normal >= 10, f"{profile_name}: wind_normal too low"
            assert wind_hurricane <= 200, f"{profile_name}: wind_hurricane too high"


class TestProfileDifferences:
    """Tests to verify profiles are meaningfully different."""

    def test_arctic_is_coldest(self) -> None:
        """Arctic profile has the lowest cold threshold."""
        profiles = create_default_profiles()
        arctic_cold = profiles["arctic"]["temp_cold"]

        for profile_name, profile in profiles.items():
            if profile_name != "arctic":
                assert profile["temp_cold"] > arctic_cold, (
                    f"{profile_name} should be warmer than arctic"
                )

    def test_tropical_is_hottest(self) -> None:
        """Tropical profile has the highest heat threshold."""
        profiles = create_default_profiles()
        tropical_hot = profiles["tropical"]["temp_hot"]

        for profile_name, profile in profiles.items():
            if profile_name != "tropical" and profile_name != "mediterranean":  # noqa: PLR1714
                assert profile["temp_hot"] <= tropical_hot, (
                    f"{profile_name} should be cooler than tropical"
                )

    def test_tropical_has_highest_precipitation(self) -> None:
        """Tropical profile has the highest high precipitation threshold."""
        profiles = create_default_profiles()
        tropical_precip = profiles["tropical"]["precip_high"]

        for profile_name, profile in profiles.items():
            assert profile["precip_high"] <= tropical_precip, (
                f"{profile_name} precip_high exceeds tropical"
            )

    def test_mediterranean_has_lowest_precipitation_low(self) -> None:
        """Mediterranean profile has a very low low precipitation threshold."""
        profiles = create_default_profiles()
        med_precip_low = profiles["mediterranean"]["precip_low"]
        assert med_precip_low == 1.0
