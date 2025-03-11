# SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>
# SPDX-FileCopyrightText: [year] [copyright holder] <[email address]>
#
# SPDX-License-Identifier: MIT

from typing import Any

import pytest
from pytheca.errors import SettingError
from pytheca.settings import EnvSettingsProvider, SettingsProvider


class TestSettingsProvider:
    class BlankSettingsProvider(SettingsProvider):
        def get_setting_value(
            self, setting_identifier: str, setting_type: Any, default_value: Any = None
        ) -> Any:
            raise NotImplementedError()

    @pytest.fixture()
    def blank_provider(self) -> BlankSettingsProvider:
        return TestSettingsProvider.BlankSettingsProvider()

    @pytest.mark.parametrize(
        "identifier",
        ["a", "abc", ".abc5", "A.B.", "A.B.C.5", "A.C", "AB", "A-B"],
    )
    def test_check_identifier(
        self, blank_provider: BlankSettingsProvider, identifier: str
    ) -> None:
        blank_provider.check_identifier(identifier)

    @pytest.mark.parametrize("identifier", ["", ".", "-", "A/", "B.C%"])
    def test_invalid_identifier(
        self, blank_provider: BlankSettingsProvider, identifier: str
    ) -> None:
        with pytest.raises(
            SettingError,
            match=f"The requested identifier '{identifier}' does not follow the identifier format.",
        ) as exc_info:
            blank_provider.check_identifier(identifier)
        assert exc_info.value.setting_identifier == identifier
        assert exc_info.value.setting_type is None


class TestEnvSettingsProvider:
    def test_instantiation_no_arguments(self) -> None:
        EnvSettingsProvider()

    @pytest.mark.parametrize(
        "value,setting_type,expected",
        [
            ("5", int, 5),
            ("some string", str, "some string"),
            ("some string", bool, True),
            ("False", bool, True),
            ("", bool, False),
            ("1.0", float, 1.0),
            ("1.9", float, 1.9),
            ("10", float, 10.0),
        ],
    )
    def test_get_settings_value_type_casting(
        self, monkeypatch: Any, value: str, setting_type: type, expected: Any
    ) -> None:
        settings_provider = EnvSettingsProvider()
        monkeypatch.setenv("FOO", value)
        assert settings_provider.get_setting_value("FOO", setting_type) == expected

    def test_get_settings_value_complex_identifier(self, monkeypatch: Any) -> None:
        settings_provider = EnvSettingsProvider()
        monkeypatch.setenv("A_B_C", "FOO")
        assert settings_provider.get_setting_value("a.b.c", str) == "FOO"

    def test_get_settings_type_not_supported(self, monkeypatch: Any) -> None:
        class SomeType: ...

        settings_provider = EnvSettingsProvider()
        monkeypatch.setenv("FOO", "5")
        with pytest.raises(
            SettingError,
            match=f"{SomeType} requested for FOO not supported by SettingProvider.",
        ):
            settings_provider.get_setting_value("FOO", SomeType)

    @pytest.mark.parametrize(
        "value,setting_type,expected_error_msg",
        [
            ("True", int, "Error converting True to <class 'int'> requested for foo."),
            ("1.0", int, "Error converting 1.0 to <class 'int'> requested for foo."),
            (
                "some string",
                float,
                "Error converting some string to <class 'float'> requested for foo.",
            ),
        ],
    )
    def test_unsuccessful_conversion(
        self, monkeypatch: Any, value: Any, setting_type: type, expected_error_msg: str
    ) -> None:
        settings_provider = EnvSettingsProvider()
        monkeypatch.setenv("FOO", value)
        with pytest.raises(SettingError, match=expected_error_msg):
            settings_provider.get_setting_value("foo", setting_type)

    def test_no_default_value(self, monkeypatch: Any) -> None:
        settings_provider = EnvSettingsProvider()
        with pytest.raises(SettingError, match="No value for foo.bar could be found."):
            settings_provider.get_setting_value("foo.bar", int)

    def test_default_value(self, monkeypatch: Any) -> None:
        settings_provider = EnvSettingsProvider()
        assert settings_provider.get_setting_value("foo.bar", int, 5) == 5
