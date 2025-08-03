"""
Copyright (C) 2015 Square, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Modified by Matthew Au-Yeung on 2025-07-29; see changelog.md for more details.
- Similar APIs ported from Java to Python.
"""

from typing import Annotated, Literal

from pyjavapoet.type_name import ClassName, TypeName


class Constant(str):
    def __new__(cls, value: str):
        return str.__new__(cls, value)


EMPTY_STRING = Constant("")


class CodeWriter:
    """
    Handles emitting Java code with proper formatting.
    """

    __indent: str
    # TODO: __max_line_length: int
    __out: list[str]
    __indent_level: int
    __line_start: bool

    # Track ClassNames that have been used. If it maps to a None that means
    # it's a part of the current package.
    __imports: dict[Annotated[str, "top_level_simple_name"], ClassName]

    # Track all the classes available in the current class scope
    # They will take priority over any named reference
    # The value is the number of times it has been excluded
    __excluded_scoped_classes: dict[str, int]

    __package_name: str

    def __init__(self, indent: str = "  ", type_spec_class_name: ClassName | None = None):
        self.__indent = indent
        self.__out = []  # Output buffer
        self.__indent_level = 0
        self.__line_start = True  # Are we at the start of a line?
        self.__package_name = ""
        self.__imports = {}
        self.__excluded_scoped_classes = {}

        # Imports tracking
        if type_spec_class_name:
            self.__package_name = type_spec_class_name.package_name
            self.__excluded_scoped_classes[type_spec_class_name.top_simple_name] = 1

    def indent(self, count: int = 1) -> None:
        self.__indent_level += count

    def unindent(self, count: int = 1) -> None:
        if self.__indent_level > 0:
            self.__indent_level -= min(count, self.__indent_level)

    def emit(self, s: str | Constant, new_line_prefix: str = "") -> "CodeWriter":
        if s.startswith("\n"):
            if self.__line_start and new_line_prefix:
                self.__out.append(self.__indent * self.__indent_level)
                self.__out.append(new_line_prefix)

            # Reset line start
            self.__out.append("\n")
            self.__line_start = True
            s = s[1:]

        if not s and not isinstance(s, Constant):
            return self

        if self.__line_start:
            # Add indentation at start of line
            self.__out.append(self.__indent * self.__indent_level)
            self.__out.append(new_line_prefix)
            self.__line_start = False

        # Split by newlines to handle indentation
        lines = s.split("\n")
        for i, line in enumerate(lines):
            if i > 0:
                # Emit newline and indentation
                self.emit(f"\n{line}", new_line_prefix)
            else:
                # Emit the line
                self.__out.append(line)

        # Update line start flag
        if s.endswith("\n"):
            self.__line_start = True

        return self

    def emit_type(self, type_name: "TypeName") -> None:
        if isinstance(type_name, ClassName):
            # Record that we need to import this type
            # Note: in_package also includes primitive types :)
            package_name = type_name.package_name or self.__package_name
            in_package_or_primitive = package_name == self.__package_name or type_name.is_primitive()
            is_excluded = self.__excluded_scoped_classes.get(type_name.top_simple_name, 0) > 0
            class_name = self.__imports.get(type_name.top_simple_name)
            if not in_package_or_primitive and not is_excluded and (not class_name or type_name == class_name):
                self.emit(type_name.nested_name)
                self.__imports[type_name.top_simple_name] = type_name
            elif in_package_or_primitive and not class_name:
                # This means we haven't imported this top_simple_name yet
                # So we can use the nested_name and exclude it from the imports
                self.emit(type_name.nested_name)
                self.exclude_scoped_class(type_name.top_simple_name)
            else:
                self.emit(type_name.canonical_name)
        else:
            type_name.emit(self)

    def begin_control_flow(
        self,
        control_flow_string: Literal["if", "for", "while", "switch", "try", "catch", "finally"],
    ) -> "CodeWriter":
        self.emit(control_flow_string)
        self.emit(" {\n")
        self.indent()
        return self

    def next_control_flow(
        self,
        control_flow_string: Literal["else", "else if", "case", "default"],
    ) -> "CodeWriter":
        self.unindent()
        self.emit("} ")
        self.emit(control_flow_string)
        self.emit(" {\n")
        self.indent()
        return self

    def end_control_flow(self) -> "CodeWriter":
        self.unindent()
        self.emit("}\n")
        return self

    def exclude_scoped_class(self, class_name: str):
        """
        Define any inner classes here because any usage on the same level
        inherently references them
        """
        self.__excluded_scoped_classes[class_name] = self.__excluded_scoped_classes.get(class_name, 0) + 1

    def unexclude_scoped_class(self, class_name: str):
        self.__excluded_scoped_classes[class_name] = self.__excluded_scoped_classes.get(class_name, 0) - 1
        if self.__excluded_scoped_classes[class_name] < 0:
            raise ValueError(f"Class {class_name} has been unexcluded more times than it was excluded")

    def get_imports(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}

        for type_name in self.__imports.values():
            package = type_name.package_name
            if type_name.ignore_import:
                continue

            if package not in result:
                result[package] = set()
            result[package].add(type_name.simple_name)

        return result

    def __str__(self) -> str:
        return "".join(self.__out)
