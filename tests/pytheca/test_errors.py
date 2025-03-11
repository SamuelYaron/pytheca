# SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>
# SPDX-FileCopyrightText: [year] [copyright holder] <[email address]>
#
# SPDX-License-Identifier: MIT

from pytheca.errors import SettingError, RegistryError
import pytest


def test_registry_error() -> None:
    with pytest.raises(RegistryError, match="MESSAGE"):
        raise RegistryError("MESSAGE")


def test_setting_error() -> None:
    with pytest.raises(SettingError, match="MESSAGE") as exc_info:
        raise SettingError("MESSAGE", "identifier", int)
    assert exc_info.value.setting_type is int
    assert exc_info.value.setting_identifier == "identifier"
