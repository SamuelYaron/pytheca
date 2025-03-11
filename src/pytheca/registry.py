# SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>
# SPDX-FileCopyrightText: [year] [copyright holder] <[email address]>
#
# SPDX-License-Identifier: MIT

from typing import Any, NamedTuple, get_type_hints, Annotated

from .settings import SettingsProvider, EnvSettingsProvider, SettingDetails

from .errors import RegistryError


class _InterfaceDetails(NamedTuple):
    name: str
    interface_cls: type


class ImplementationDetails(NamedTuple):
    implementation_cls: type


class _RegistryEntry(NamedTuple):
    interface_details: _InterfaceDetails
    implementation_details: ImplementationDetails | None


class Registry:
    """
    Registry provides an object, where you can register interfaces and corresponding implementations.
    """

    settings_provider: Annotated[
        SettingsProvider, ImplementationDetails(implementation_cls=EnvSettingsProvider)
    ]

    def __init__(
        self,
    ) -> None:
        super().__setattr__("_interfaces", {})
        type_hints = get_type_hints(self.__class__, include_extras=True)
        for name, annotation in type_hints.items():
            metadata: tuple[Any, ...] = getattr(annotation, "__metadata__", tuple())
            origin_class = getattr(annotation, "__origin__", None)
            if (
                len(metadata) == 0
                or not isinstance(metadata[0], ImplementationDetails)
                or not origin_class
            ):
                continue
            self.register_interface(
                name, origin_class, implementation_details=metadata[0]
            )

    def __getattr__(self, name: str) -> Any:
        if name not in self._interfaces:
            raise RegistryError(f"The attribute {name} could not be found.")
        implementation_details = self._interfaces[name].implementation_details
        if implementation_details is None:
            raise RegistryError(f"The interface {name} has no implementation details.")
        return self.__instantiate_interface_instance(
            implementation_details.implementation_cls
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._interfaces and isinstance(value, ImplementationDetails):
            self.register_interface(
                name,
                self._interfaces[name].interface_details.interface_cls,
                implementation_details=value,
            )
        elif name in self._interfaces and not isinstance(value, ImplementationDetails):
            raise RegistryError(
                f"The value for setting the attribute {name} must be an instance of ImplementationDetails.",
            )
        else:
            super().__setattr__(name, value)

    def __instantiate_interface_instance(self, cls_object: type) -> Any:
        type_hints = get_type_hints(
            getattr(cls_object, "__init__", None), include_extras=True
        )
        kwargs = {}
        for setting_name, annotation in type_hints.items():
            metadata: tuple[Any, ...] = getattr(annotation, "__metadata__", tuple())
            setting_type = getattr(annotation, "__origin__", None)
            if (
                len(metadata) == 0
                or not isinstance(metadata[0], SettingDetails)
                or not setting_type
            ):
                continue
            setting_details: SettingDetails = metadata[0]
            kwargs[setting_name] = self.settings_provider.get_setting_value(
                setting_details.identifier, setting_type, setting_details.default_value
            )
        return cls_object(**kwargs)

    def register_interface(
        self,
        name: str,
        interface_cls: type,
        /,
        *,
        implementation_details: ImplementationDetails | None = None,
    ) -> None:
        """
        Registers a new interface to the registry.

        :param name: The name of the new interface. Must be a valid python identifier.
        :param interface_cls: The interface class to register.
        :param implementation_details: An optional instance of implementation details.
        """
        if implementation_details and not issubclass(
            implementation_details.implementation_cls, interface_cls
        ):
            raise RegistryError(
                f"The implementation class {implementation_details.implementation_cls} must be a subclass of the interface class {interface_cls}."
            )
        self._interfaces[name] = _RegistryEntry(
            _InterfaceDetails(name, interface_cls), implementation_details
        )
