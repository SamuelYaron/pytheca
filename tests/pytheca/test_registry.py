# SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>
# SPDX-FileCopyrightText: [year] [copyright holder] <[email address]>
#
# SPDX-License-Identifier: MIT

from typing import Annotated

import pytest
from pytheca.errors import RegistryError
from pytheca.registry import (
    Registry,
    _RegistryEntry,
    _InterfaceDetails,
    ImplementationDetails,
)
from pytheca.settings import SettingsProvider, EnvSettingsProvider


class TestRegistry:
    def test_instantiation_no_arguments(self) -> None:
        registry = Registry()
        assert isinstance(registry.settings_provider, SettingsProvider)

    def test_register_interface_no_implementation(
        self, registry_instance: Registry, simple_interface: tuple[type, type]
    ) -> None:
        registry_instance.register_interface("foo", simple_interface[0])
        assert registry_instance._interfaces == {
            "foo": _RegistryEntry(_InterfaceDetails("foo", simple_interface[0]), None),
            "settings_provider": _RegistryEntry(
                _InterfaceDetails("settings_provider", SettingsProvider),
                ImplementationDetails(implementation_cls=EnvSettingsProvider),
            ),
        }

    def test_register_interface_with_implementation(
        self, registry_instance: Registry, simple_interface: tuple[type, type]
    ) -> None:
        registry_instance.register_interface(
            "foo",
            simple_interface[0],
            implementation_details=ImplementationDetails(simple_interface[1]),
        )
        assert registry_instance._interfaces == {
            "foo": _RegistryEntry(
                _InterfaceDetails("foo", simple_interface[0]),
                ImplementationDetails(simple_interface[1]),
            ),
            "settings_provider": _RegistryEntry(
                _InterfaceDetails("settings_provider", SettingsProvider),
                ImplementationDetails(implementation_cls=EnvSettingsProvider),
            ),
        }

    def test_register_interface_existing(
        self, registry_instance: Registry, simple_interface: tuple[type, type]
    ) -> None:
        class OtherInterface: ...

        registry_instance.register_interface("foo", simple_interface[0])
        registry_instance.register_interface("foo", OtherInterface)
        assert registry_instance._interfaces == {
            "foo": _RegistryEntry(_InterfaceDetails("foo", OtherInterface), None),
            "settings_provider": _RegistryEntry(
                _InterfaceDetails("settings_provider", SettingsProvider),
                ImplementationDetails(implementation_cls=EnvSettingsProvider),
            ),
        }

    def test_register_interface_wrong_implementation_class(
        self, registry_instance: Registry, simple_interface: tuple[type, type]
    ) -> None:
        class OtherImplementation: ...

        with pytest.raises(
            RegistryError,
            match=f"The implementation class {OtherImplementation} must be a subclass of the interface class {simple_interface[0]}.",
        ):
            registry_instance.register_interface(
                "foo",
                simple_interface[0],
                implementation_details=ImplementationDetails(OtherImplementation),
            )

    def test_get_interface_implementation(
        self, simple_registry_instance: Registry, simple_interface: tuple[type, type]
    ) -> None:
        assert isinstance(simple_registry_instance.myinterface, simple_interface[1])

    def test_get_interface_implementation_no_interface(
        self, simple_registry_instance: Registry
    ) -> None:
        with pytest.raises(
            RegistryError, match="The attribute foo could not be found."
        ):
            simple_registry_instance.foo

    def test_get_interface_implementation_no_implementation(
        self, registry_instance: Registry, simple_interface: tuple[type, type]
    ) -> None:
        registry_instance.register_interface("foo", simple_interface[0])
        with pytest.raises(
            RegistryError, match="The interface foo has no implementation details."
        ):
            registry_instance.foo

    def test_set_interface_implementation(
        self, registry_instance: Registry, simple_interface: tuple[type, type]
    ) -> None:
        registry_instance.register_interface("foo", simple_interface[0])
        registry_instance.foo = ImplementationDetails(simple_interface[1])
        assert isinstance(registry_instance.foo, simple_interface[1])

    def test_set_interface_implementation_wrong_implementation_class(
        self, registry_instance: Registry, simple_interface: tuple[type, type]
    ) -> None:
        class OtherImplementation: ...

        registry_instance.register_interface("foo", simple_interface[0])
        with pytest.raises(
            RegistryError,
            match=f"The implementation class {OtherImplementation} must be a subclass of the interface class {simple_interface[0]}.",
        ):
            registry_instance.foo = ImplementationDetails(OtherImplementation)

    def test_set_interface_implementation_arbitrary_value(
        self, simple_registry_instance: Registry
    ) -> None:
        with pytest.raises(
            RegistryError,
            match="The value for setting the attribute myinterface must be an instance of ImplementationDetails.",
        ):
            simple_registry_instance.myinterface = 5

    def test_set_arbitrary_attribute(self, registry_instance: Registry) -> None:
        registry_instance.foo = 5
        assert registry_instance.foo == 5


class TestRegistryDeclarative:
    def test_definition(self) -> None:
        class SimpleInterface:
            pass

        class SimpleImplementation(SimpleInterface):
            pass

        class MyRegistry(Registry):
            my_interface: Annotated[
                SimpleInterface, ImplementationDetails(SimpleImplementation)
            ]

        registry = MyRegistry()
        assert isinstance(registry.my_interface, SimpleImplementation)

    def test_arbitrary_cls_attributes(self) -> None:
        class MyRegistry(Registry):
            typed_default: int = 5
            untyped_default = ""
            typed: str
            annotated: Annotated[int, "some metadata"] = 5

        MyRegistry()

    def test_wrong_implementation_cls(self) -> None:
        class SimpleInterface:
            pass

        class OtherImpl: ...

        class MyRegistry(Registry):
            my_interface: Annotated[SimpleInterface, ImplementationDetails(OtherImpl)]

        with pytest.raises(
            RegistryError,
            match=f"The implementation class {OtherImpl} must be a subclass of the interface class {SimpleInterface}.",
        ):
            MyRegistry()
