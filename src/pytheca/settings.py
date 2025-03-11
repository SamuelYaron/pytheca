# SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>
# SPDX-FileCopyrightText: [year] [copyright holder] <[email address]>
#
# SPDX-License-Identifier: MIT

import os
from abc import ABC, abstractmethod
from typing import Any, NamedTuple

from .errors import SettingError


class SettingDetails(NamedTuple):
    identifier: str
    default_value: Any = None


class SettingsProvider(ABC):
    """
    An interface that provides a method to retrieve settings.

    The implementing class needs to implement the means of setting retrieval.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def check_identifier(identifier: str) -> None:
        """
        Function to check if a given string is a valid setting identifier.
        :param identifier: The string to check.
        :raises SettingError: If the string is not a valid identifier.
        """
        if not identifier.replace(".", "").replace("-", "").isalnum():
            raise SettingError(
                f"The requested identifier '{identifier}' does not follow the identifier format.",
                identifier,
            )

    @abstractmethod
    def get_setting_value(
        self, setting_identifier: str, setting_type: type, default_value: Any = None
    ) -> Any:
        """
        Method to retrieve a value for a given setting identifier.
        :param setting_identifier: The identifier to retrieve the value for.
        :param setting_type: The python type the value should have.
        :param default_value: The default value to return if the setting could not be found.
        :return: The value of the setting.
        :raises SettingError: Can be raised if:
        - the identifier is invalid.
        - no value for the identifier could be found.
        - the desired type is not supported by the SettingsProvider.
        - the value could not be cast to the desired type.
        """


class EnvSettingsProvider(SettingsProvider):
    def convert_identifier(self, identifier: str) -> str:
        self.check_identifier(identifier)
        return identifier.upper().replace(".", "_")

    def get_setting_value(
        self, setting_identifier: str, setting_type: type, default_value: Any = None
    ) -> Any:
        raw_value = os.getenv(self.convert_identifier(setting_identifier), None)
        if raw_value is not None:
            try:
                if setting_type is int:
                    return int(raw_value)
                elif setting_type is str:
                    return raw_value
                elif setting_type is bool:
                    return bool(raw_value)
                elif setting_type is float:
                    return float(raw_value)
                else:
                    raise SettingError(
                        f"{setting_type} requested for {setting_identifier} not supported by SettingProvider.",
                        setting_identifier,
                        setting_type,
                    )
            except ValueError as exc:
                raise SettingError(
                    f"Error converting {raw_value} to {setting_type} requested for {setting_identifier}.",
                    setting_identifier,
                    setting_type,
                ) from exc
        elif default_value is None:
            raise SettingError(
                f"No value for {setting_identifier} could be found.",
                setting_identifier,
                setting_type,
            )
        else:
            return default_value
