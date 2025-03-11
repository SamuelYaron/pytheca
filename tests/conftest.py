# SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>
#
# SPDX-License-Identifier: MIT

import pytest
from pytheca.registry import Registry, ImplementationDetails


@pytest.fixture
def registry_instance() -> Registry:
    return Registry()


@pytest.fixture
def simple_interface() -> tuple[type, type]:
    class SimpleInterface:
        pass

    class SimpleImplementation(SimpleInterface):
        pass

    return SimpleInterface, SimpleImplementation


@pytest.fixture
def simple_registry_instance(simple_interface: tuple[type, type]) -> Registry:
    registry = Registry()
    registry.register_interface(
        "myinterface",
        simple_interface[0],
        implementation_details=ImplementationDetails(simple_interface[1]),
    )
    return registry
