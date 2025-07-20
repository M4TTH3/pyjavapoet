"""
Utility classes for writing Java code.

This module defines:
- LineWrapper: Handles line wrapping and indentation
- CodeWriter: Handles emitting Java code with proper formatting
"""

from typing import Dict, Set, Union

from pyjavapoet.type_name import TypeName


class LineWrapper:
    """
    Helper class for CodeWriter that handles line wrapping.
    """

    def __init__(self, code_writer: "CodeWriter", indent_level: int, max_line_length: int):
        self.code_writer = code_writer
        self.indent_level = indent_level
        self.max_line_length = max_line_length
        self.current_line_length = 0
        self.need_wrap = False

    def append(self, s: str) -> None:
        if s.startswith("\n"):
            # Reset for newline
            self.current_line_length = 0
            self.code_writer.emit(s)
            return

        # Check if we need to wrap
        if self.current_line_length + len(s) > self.max_line_length:
            self.code_writer.emit("\n" + "  " * self.indent_level)
            self.current_line_length = 2 * self.indent_level

        self.code_writer.emit(s)
        self.current_line_length += len(s)


class CodeWriter:
    """
    Handles emitting Java code with proper formatting.
    """

    def __init__(self, indent: str = "  ", max_line_length: int = 100):
        self.indent = indent
        self.max_line_length = max_line_length
        self.out = []  # Output buffer
        self.indent_level = 0
        self.line_start = True  # Are we at the start of a line?

        # Imports tracking
        self.imports = set()  # Set of imports that must be added

    def indent_more(self) -> None:
        self.indent_level += 1

    def indent_less(self) -> None:
        if self.indent_level > 0:
            self.indent_level -= 1

    def emit(self, s: str) -> "CodeWriter":
        if s.startswith("\n"):
            # Reset line start
            self.out.append("\n")
            self.line_start = True
            s = s[1:]

        if not s:
            return self

        if self.line_start:
            # Add indentation at start of line
            self.out.append(self.indent * self.indent_level)
            self.line_start = False

        # Split by newlines to handle indentation
        lines = s.split("\n")
        for i, line in enumerate(lines):
            if i > 0:
                # Emit newline and indentation
                self.out.append("\n")
                if line:  # Only indent non-empty lines
                    self.out.append(self.indent * self.indent_level)

            # Emit the line
            self.out.append(line)

        # Update line start flag
        if s.endswith("\n"):
            self.line_start = True

        return self

    def emit_statement(self, format_string: str, *args) -> "CodeWriter":
        # Format the statement
        from pyjavapoet.code_block import CodeBlock

        code_block = CodeBlock.of(format_string, *args)
        code_block.emit(self)

        # Add semicolon and newline
        self.emit(";\n")
        return self

    def emit_type(self, type_name: Union["TypeName", str]) -> None:
        if isinstance(type_name, str):
            # Convert string to TypeName
            from pyjavapoet.type_name import TypeName

            type_name = TypeName.get(type_name)

        # Handle imports for class names
        from pyjavapoet.type_name import ClassName

        if isinstance(type_name, ClassName):
            # Record that we need to import this type
            if type_name.package_name:
                self.imports.add(type_name)

            self.emit(type_name.simple_name)
        else:
            type_name.emit(self)

    def begin_control_flow(self, control_flow_string: str) -> "CodeWriter":
        self.emit(control_flow_string)
        self.emit(" {\n")
        self.indent_more()
        return self

    def next_control_flow(self, control_flow_string: str) -> "CodeWriter":
        self.indent_less()
        self.emit("} ")
        self.emit(control_flow_string)
        self.emit(" {\n")
        self.indent_more()
        return self

    def end_control_flow(self) -> "CodeWriter":
        self.indent_less()
        self.emit("}\n")
        return self

    def get_imports(self) -> Dict[str, Set[str]]:
        result = {}

        # Group imports by package
        from pyjavapoet.type_name import ClassName

        for type_name in self.imports:
            if isinstance(type_name, ClassName) and type_name.package_name:
                package = type_name.package_name
                if package not in result:
                    result[package] = set()
                result[package].add(type_name.simple_name)

        return result

    def line_wrapper(self) -> LineWrapper:
        return LineWrapper(self, self.indent_level, self.max_line_length)

    def __str__(self) -> str:
        return "".join(self.out)
