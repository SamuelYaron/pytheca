# SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>
# SPDX-FileCopyrightText: [year] [copyright holder] <[email address]>
#
# SPDX-License-Identifier: MIT

from typing import Annotated, Any

from pytheca import ImplementationDetails, Registry
from pytheca.settings import SettingDetails


def test_interface_with_settings(registry_instance: Registry, monkeypatch: Any) -> None:
    class MyInterface:
        def return_str(self) -> str:
            return ""

    class MyImplementation(MyInterface):
        def __init__(
            self, return_value: Annotated[str, SettingDetails("foo.bar")]
        ) -> None:
            self.return_value = return_value

        def return_str(self) -> str:
            return self.return_value

    registry_instance.register_interface(
        "interface",
        MyInterface,
        implementation_details=ImplementationDetails(
            implementation_cls=MyImplementation
        ),
    )
    monkeypatch.setenv("FOO_BAR", "SOME STRING")
    assert registry_instance.interface.return_str() == "SOME STRING"
