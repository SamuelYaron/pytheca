<!--
SPDX-FileCopyrightText: 2025 SamuelYaron <samuel.yaron@oxur.de>

SPDX-License-Identifier: MIT
-->

# Pytheca

This project is still very much a WIP and not yet intended for any productive use.

A more detailed documentation will follow soon.

## Usage

To use pytheca you can either create a dynamic Registry or create your own declarative registry class.

### Dynamic usage

```python
from abc import abstractmethod, ABC
from pytheca import Registry, ImplementationDetails

# Create interface definition as a class.
class MyInterface(ABC):
    @abstractmethod
    def print_message(self, message: str) -> None: ...

# Create interface implementation.
class UpperPrinter(MyInterface):
    def print_message(self, message: str) -> None:
        print(message.upper())

# Create registry object
my_registry = Registry()
# Register your interface
my_registry.register_interface("printer", MyInterface, implementation_details=ImplementationDetails(implementation_cls=UpperPrinter))
# Use interface
my_registry.printer.print_message("Hi!")
# >>> HI!

# Define another interface implementation and set it as the new interface implementation
class LowerPrinter(MyInterface):
    def print_message(self, message: str) -> None:
        print(message.lower())

my_registry.printer = ImplementationDetails(implementation_cls=LowerPrinter)
my_registry.printer.print_message("Hi!")
# >>> hi!
```

### Declarative usage

```python
from abc import abstractmethod, ABC
from typing import Annotated
from pytheca import Registry, ImplementationDetails

# Create interface definition as a class.
class MyInterface(ABC):
    @abstractmethod
    def print_message(self, message: str) -> None: ...

# Create interface implementation.
class UpperPrinter(MyInterface):
    def print_message(self, message: str) -> None:
        print(message.upper())

# Create declarative registry class.
class MyRegistry(Registry):
    printer: Annotated[MyInterface, ImplementationDetails(implementation_cls=UpperPrinter)]
# Create registry object
my_registry = MyRegistry()
# Use interface
my_registry.printer.print_message("Hi!")
# >>> HI!

# Define another interface implementation and set it as the new interface implementation (still works on delcarative registries)
class LowerPrinter(MyInterface):
    def print_message(self, message: str) -> None:
        print(message.lower())

my_registry.printer = ImplementationDetails(implementation_cls=LowerPrinter)
my_registry.printer.print_message("Hi!")
# >>> hi!
```

### Create Interface implementations with settings

```python
from abc import abstractmethod, ABC
from typing import Annotated
from pytheca import Registry, ImplementationDetails, SettingDetails

# Create interface definition as a class.
class MyInterface(ABC):
    @abstractmethod
    def print_message(self, message: str) -> None: ...

# Create interface implementation.
class UpperPrinter(MyInterface):
    def __init__(self, suffix: Annotated[str, SettingDetails(identifier="upper-printer.suffix")]):
        self.suffix = suffix

    def print_message(self, message: str) -> None:
        print(f"{message.upper()}{self.suffix}")

# Create registry object
my_registry = Registry()
# Register your interface
my_registry.register_interface("printer", MyInterface, implementation_details=ImplementationDetails(implementation_cls=UpperPrinter))
# Inject environment variable
import os
os.environ["UPPER-PRINTER_SUFFIX"] = "-some suffix"
# Use interface
my_registry.printer.print_message("Hi!")
# >>> HI!-some suffix
```
