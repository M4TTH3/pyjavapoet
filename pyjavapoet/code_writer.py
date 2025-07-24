"""
Utility classes for writing Java code.

This module defines:
- LineWrapper: Handles line wrapping and indentation
- CodeWriter: Handles emitting Java code with proper formatting
"""

from typing import Literal

from pyjavapoet.type_name import ClassName, TypeName


class CodeWriter:
    """
    Handles emitting Java code with proper formatting.
    """

    __indent: str
    __max_line_length: int # TODO
    __out: list[str]
    __indent_level: int
    __line_start: bool
    __imports: set[str]

    def __init__(self, indent: str = "  "):
        self.__indent = indent
        self.__out = []  # Output buffer
        self.__indent_level = 0
        self.__line_start = True  # Are we at the start of a line?

        # Imports tracking
        self.__imports = set()  # Set of imports that must be added

    def indent(self, count: int = 1) -> None:
        self.__indent_level += count

    def unindent(self, count: int = 1) -> None:
        if self.__indent_level > 0:
            self.__indent_level -= min(count, self.__indent_level)

    def emit(self, s: str, new_line_prefix: str = "") -> "CodeWriter":
        if s.startswith("\n"):
            # Reset line start
            self.__out.append("\n")
            self.__line_start = True
            s = s[1:]

        if not s:
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
            if type_name.package_name and not type_name.ignore_package_name:
                self.__imports.add(type_name)

            self.emit(type_name.nested_name)
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

    def get_imports(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}

        for type_name in self.__imports:
            if isinstance(type_name, ClassName) and type_name.package_name:
                package = type_name.package_name
                if package not in result:
                    result[package] = set()
                result[package].add(type_name.simple_name)

        return result

    def __str__(self) -> str:
        return "".join(self.__out)
