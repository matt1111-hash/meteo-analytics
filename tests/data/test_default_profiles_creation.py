"""Default anomaly profiles tests."""

from __future__ import annotations

from datetime import datetime

from src.data.anomaly_profile.default_profiles import (
    create_default_profiles,
    create_profiles_data,
)


class TestCreateDefaultProfiles:
    """Tests for create_default_profiles function."""

    def test_returns_dict(self) -> None:
        """create_default_profiles returns a dictionary."""
        profiles = create_default_profiles()
        assert isinstance(profiles, dict)

    def test_contains_all_expected_profiles(self) -> None:
        """All expected profile keys are present."""
        profiles = create_default_profiles()
        expected_keys = {
            "default",
            "tropical",
            "arctic",
            "continental",
            "mediterranean",
        }
        assert set(profiles.keys()) == expected_keys

    def test_default_profile_structure(self) -> None:
        """Default profile has correct structure and values."""
        profiles = create_default_profiles()
        default_profile = profiles["default"]

        assert "profile_name" in default_profile
        assert "description" in default_profile
        assert "temp_hot" in default_profile
        assert "temp_cold" in default_profile
        assert "precip_high" in default_profile
        assert "precip_low" in default_profile
        assert default_profile["profile_name"] == "default"
        assert default_profile["temp_hot"] == 35.0
        assert default_profile["temp_cold"] == -10.0

    def test_tropical_profile_values(self) -> None:
        """Tropical profile has climate-appropriate values."""
        profiles = create_default_profiles()
        tropical = profiles["tropical"]

        assert tropical["profile_name"] == "tropical"
        assert tropical["temp_hot"] == 40.0
        assert tropical["temp_cold"] == 10.0
        assert tropical["precip_high"] == 200.0
        assert tropical["precip_low"] == 2.0
        assert tropical["wind_hurricane"] == 150.0

    def test_arctic_profile_values(self) -> None:
        """Arctic profile has climate-appropriate values."""
        profiles = create_default_profiles()
        arctic = profiles["arctic"]

        assert arctic["profile_name"] == "arctic"
        assert arctic["temp_hot"] == 25.0
        assert arctic["temp_cold"] == -30.0
        assert arctic["precip_high"] == 50.0
        assert arctic["precip_low"] == 1.0
        assert arctic["wind_extreme"] == 80.0
        assert arctic["wind_hurricane"] == 100.0

    def test_continental_profile_values(self) -> None:
        """Continental profile has climate-appropriate values."""
        profiles = create_default_profiles()
        continental = profiles["continental"]

        assert continental["profile_name"] == "continental"
        assert continental["temp_hot"] == 38.0
        assert continental["temp_cold"] == -20.0
        assert continental["precip_high"] == 120.0
        assert continental["precip_low"] == 3.0
        assert continental["wind_strong"] == 80.0
        assert continental["wind_extreme"] == 110.0

    def test_mediterranean_profile_values(self) -> None:
        """Mediterranean profile has climate-appropriate values."""
        profiles = create_default_profiles()
        mediterranean = profiles["mediterranean"]

        assert mediterranean["profile_name"] == "mediterranean"
        assert mediterranean["temp_hot"] == 42.0
        assert mediterranean["temp_cold"] == 0.0
        assert mediterranean["precip_high"] == 80.0
        assert mediterranean["precip_low"] == 1.0
        assert mediterranean["wind_normal"] == 40.0
        assert mediterranean["wind_strong"] == 60.0

    def test_all_profiles_have_required_fields(self) -> None:
        """All profiles have the same required fields."""
        profiles = create_default_profiles()
        required_fields = {
            "profile_name",
            "description",
            "temp_hot",
            "temp_cold",
            "precip_high",
            "precip_low",
            "wind_normal",
            "wind_strong",
            "wind_extreme",
            "wind_hurricane",
        }

        for profile_name, profile_data in profiles.items():
            missing_fields = required_fields - set(profile_data.keys())
            assert not missing_fields, f"{profile_name} missing fields: {missing_fields}"

    def test_all_profiles_have_timestamps(self) -> None:
        """All profiles have created_at and modified_at timestamps."""
        profiles = create_default_profiles()

        for profile_data in profiles.values():
            assert "created_at" in profile_data
            assert "modified_at" in profile_data
            datetime.fromisoformat(profile_data["created_at"])
            datetime.fromisoformat(profile_data["modified_at"])

    def test_descriptions_are_in_hungarian(self) -> None:
        """Profile descriptions are in Hungarian."""
        profiles = create_default_profiles()

        assert "klímájú" in profiles["default"]["description"]
        assert "tropikus" in profiles["tropical"]["description"].lower()
        assert "sarkvidéki" in profiles["arctic"]["description"].lower()
        assert "kontinentális" in profiles["continental"]["description"].lower()
        assert "mediterrán" in profiles["mediterranean"]["description"].lower()


class TestCreateProfilesData:
    """Tests for create_profiles_data function."""

    def test_returns_dict(self) -> None:
        """create_profiles_data returns a dictionary."""
        data = create_profiles_data()
        assert isinstance(data, dict)

    def test_contains_profiles_key(self) -> None:
        """Result contains 'profiles' key."""
        data = create_profiles_data()
        assert "profiles" in data

    def test_contains_active_profile_key(self) -> None:
        """Result contains 'active_profile' key."""
        data = create_profiles_data()
        assert "active_profile" in data

    def test_contains_created_at_key(self) -> None:
        """Result contains 'created_at' key."""
        data = create_profiles_data()
        assert "created_at" in data

    def test_contains_version_key(self) -> None:
        """Result contains 'version' key."""
        data = create_profiles_data()
        assert "version" in data

    def test_default_active_profile(self) -> None:
        """Default active profile is 'default'."""
        data = create_profiles_data()
        assert data["active_profile"] == "default"

    def test_custom_active_profile(self) -> None:
        """Custom active profile can be specified."""
        data = create_profiles_data(active_profile="tropical")
        assert data["active_profile"] == "tropical"

    def test_profiles_match_default_profiles(self) -> None:
        """Profiles key contains the same profiles as create_default_profiles."""
        data = create_profiles_data()
        profiles = create_default_profiles()

        assert set(data["profiles"].keys()) == set(profiles.keys())

        for profile_name in profiles.keys():  # noqa: SIM118
            data_profile = data["profiles"][profile_name]
            default_profile = profiles[profile_name]
            for key in default_profile:
                if key not in ("created_at", "modified_at"):
                    assert (
                        data_profile[key] == default_profile[key]
                    ), f"{profile_name}.{key} mismatch"

    def test_created_at_is_valid_timestamp(self) -> None:
        """created_at is a valid ISO timestamp."""
        data = create_profiles_data()
        created_at = data["created_at"]
        parsed = datetime.fromisoformat(created_at)
        assert isinstance(parsed, datetime)

    def test_version_is_string(self) -> None:
        """Version is a string."""
        data = create_profiles_data()
        assert isinstance(data["version"], str)

    def test_version_format(self) -> None:
        """Version follows semantic versioning format."""
        data = create_profiles_data()
        version = data["version"]
        parts = version.split(".")
        assert len(parts) >= 2
        assert parts[0].isdigit()
