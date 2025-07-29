"""
Copyright (C) 2025 Matthew Au-Yeung.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from abc import ABC, abstractmethod

from pyjavapoet.code_writer import CodeWriter


class Code[C: "Code"](ABC):
    @abstractmethod
    def emit(self, code_writer: "CodeWriter") -> None: ...

    @abstractmethod
    def to_builder(self) -> "Code.Builder[C]": ...

    def copy(self) -> C:
        return self.to_builder().build()

    def __deepcopy__(self, memo: dict) -> C:
        return self.copy()

    def __copy__(self) -> C:
        return self.copy()

    def __str__(self) -> str:
        writer = CodeWriter()
        self.emit(writer)
        return str(writer)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Code):
            return False
        return str(self) == str(other)

    class Builder[T: "Code"](ABC):
        @abstractmethod
        def build(self) -> T: ...
