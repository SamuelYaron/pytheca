# SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>
# SPDX-FileCopyrightText: [year] [copyright holder] <[email address]>
#
# SPDX-License-Identifier: MIT


class PythecaError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class RegistryError(PythecaError): ...


class SettingError(PythecaError):
    def __init__(
        self, message: str, setting_identifier: str, setting_type: type | None = None
    ) -> None:
        super().__init__(message)
        self.setting_type = setting_type
        self.setting_identifier = setting_identifier
