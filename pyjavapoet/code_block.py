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

import re
from typing import Any, Optional

from pyjavapoet.code_base import Code
from pyjavapoet.code_writer import CodeWriter
from pyjavapoet.type_name import TypeName
from pyjavapoet.util import deep_copy


class CodeBlock(Code["CodeBlock"]):
    """
    CodeBlock for formatting Java code with placeholders.

    This module defines the CodeBlock class, which is a key component for
    generating code with proper formatting and handling various types of
    placeholders like $L (literals), $S (strings), $T (types), and $N (names).
    """

    format_parts: list[str]
    args: list[Any]
    named_args: dict[str, Any]

    # Matches:
    #   $L, $S, $T, $N, $<, $>
    #   $name:T, $name:L, $name:S, $name:N (named arguments)
    #   $1L, $2S, $3T, etc. (indexed arguments)
    placeholder_match = re.compile(
        r"""
        \$(
            (?P<type1>[LSTN<>])                       # $L, $S, $T, $N, $<, $>
            |                                         # or
            (?P<name>[a-zA-Z_][a-zA-Z0-9_]*)          # $name
            :                                         # :
            (?P<type2>[LSTN])                          # T, L, S, N
            |                                         # or
            (?P<index>\d+)                            # $1, $2, etc.
            (?P<type3>[LSTN<>])                     # L, S, T, N, $<, $>
        )
        """,
        re.VERBOSE,
    )

    placeholder_match_with_newlines = re.compile(
        r"""
        (
            \$(
                (?P<type1>[LSTN<>])                       # $L, $S, $T, $N, $<, $>
                |                                         # or
                (?P<name>[a-zA-Z_][a-zA-Z0-9_]*)          # $name
                :                                         # :
                (?P<type2>[LSTN])                         # T, L, S, N
                |                                         # or
                (?P<index>\d+)                            # $1, $2, etc.
                (?P<type3>[LSTN<>])                       # L, S, T, N, $<, $>
            )
            |
            (\n)                                          # or a literal newline
        )
        """,
        re.VERBOSE,
    )

    def __init__(self, format_parts: list[str], args: list[Any], named_args: dict[str, Any]):
        self.format_parts = format_parts
        self.args = args
        self.named_args = named_args

    def emit(self, code_writer: "CodeWriter", new_line_prefix: str = "") -> None:
        arg_index = 0

        for part in self.format_parts:
            # Look for placeholders like $L, $S, $T, $N
            placeholder_match = re.search(CodeBlock.placeholder_match, part)
            if placeholder_match:
                # Emit everything before the placeholder
                if placeholder_match.start() > 0:
                    code_writer.emit(part[: placeholder_match.start()], new_line_prefix)

                # Get the placeholder type
                placeholder_type = (
                    placeholder_match.group("type1")
                    or placeholder_match.group("type2")
                    or placeholder_match.group("type3")
                )
                placeholder_index = placeholder_match.group("index")
                placeholder_name = placeholder_match.group("name")

                # Handle the placeholder
                if placeholder_type == ">":  # Indent
                    count = int(placeholder_index) if placeholder_index else 1
                    code_writer.indent(count)
                elif placeholder_type == "<":  # Unindent
                    count = int(placeholder_index) if placeholder_index else 1
                    code_writer.unindent(count)
                elif arg_index < len(self.args) or placeholder_name or placeholder_index:
                    if placeholder_name:
                        if placeholder_name not in self.named_args:
                            raise KeyError(f"No argument found for placeholder {placeholder_name}")
                        arg = self.named_args[placeholder_name]
                    elif placeholder_index:
                        index = int(placeholder_index) - 1
                        if index >= len(self.args):
                            raise IndexError(f"No argument found for placeholder {placeholder_index}")
                        arg = self.args[index]
                    else:
                        arg = self.args[arg_index]
                        arg_index += 1

                    if placeholder_type == "L":  # Literal
                        if isinstance(arg, CodeBlock):
                            arg.emit(code_writer, new_line_prefix)
                        elif isinstance(arg, bool):
                            code_writer.emit(str(arg).lower())
                        else:
                            code_writer.emit(str(arg), new_line_prefix)
                    elif placeholder_type == "S":  # String
                        # Escape special characters
                        escaped = str(arg).replace("\\", "\\\\").replace('"', '\\"')
                        # Add quotes
                        code_writer.emit(f'"{escaped}"', new_line_prefix)
                    elif placeholder_type == "T":  # Type
                        # Let the CodeWriter handle type imports
                        arg = TypeName.get(arg)
                        arg.emit(code_writer)
                    elif placeholder_type == "N":  # Name
                        if hasattr(arg, "name"):
                            code_writer.emit(arg.name, new_line_prefix)
                        else:
                            code_writer.emit(str(arg), new_line_prefix)

                # Emit everything after the placeholder
                if placeholder_match.end() < len(part):
                    code_writer.emit(part[placeholder_match.end() :], new_line_prefix)
            else:
                # No placeholders, emit the whole part
                code_writer.emit(part, new_line_prefix)

    def emit_javadoc(self, code_writer: "CodeWriter") -> None:
        code_writer.emit("/**\n")
        self.emit(code_writer, " * ")
        code_writer.emit("\n", " * ")
        code_writer.emit(" */")

    def javadoc(self) -> str:
        writer = CodeWriter()
        self.emit_javadoc(writer)
        return str(writer)

    def to_builder(self) -> "Builder":
        return CodeBlock.Builder(deep_copy(self.format_parts), deep_copy(self.args), deep_copy(self.named_args))

    @staticmethod
    def of(format_string: str, *args, **kwargs) -> "CodeBlock":
        return CodeBlock.builder().add(format_string, *args, **kwargs).build()

    @staticmethod
    def builder() -> "Builder":
        return CodeBlock.Builder()

    @staticmethod
    def join_to_code(code_blocks: list["CodeBlock"], separator: str = "") -> "CodeBlock":
        builder = CodeBlock.builder()
        if not code_blocks:
            return builder.build()

        first = True
        for code_block in code_blocks:
            if not first:
                builder.add(separator)
            first = False

            builder.add("$L", code_block)

        return builder.build()

    @staticmethod
    def add_javadoc(javadoc: Optional["CodeBlock"], format_string: str, *args) -> "CodeBlock":
        if javadoc:
            return CodeBlock.join_to_code([javadoc, CodeBlock.of(format_string, *args)])
        else:
            return CodeBlock.of(format_string, *args)

    @staticmethod
    def add_javadoc_line(javadoc: Optional["CodeBlock"], format_string: str, *args) -> "CodeBlock":
        if javadoc:
            return CodeBlock.join_to_code([javadoc, CodeBlock.of(format_string, *args)], "\n")
        else:
            return CodeBlock.of(format_string, *args)

    class Builder(Code.Builder["CodeBlock"]):
        """
        Builder for CodeBlock instances.
        """

        format_parts: list[str]
        args: list[Any]
        named_args: dict[str, Any]

        # Track begin_statement, add_statement_item, and end_statement
        __statement_builder_lines = 0

        def __init__(
            self,
            format_parts: list[str] | None = None,
            args: list[Any] | None = None,
            named_args: dict[str, Any] | None = None,
        ):
            self.format_parts = format_parts or []
            self.args = args or []
            self.named_args = named_args or {}

        def add(self, format_string: str, *args, **kwargs) -> "CodeBlock.Builder":
            # Check for arguments in the format string
            matches = list(re.finditer(CodeBlock.placeholder_match_with_newlines, format_string))

            # Simple case: no arguments
            if not matches:
                self.format_parts.append(format_string)
                return self

            # Complex case: handle placeholders
            last_end = 0
            for match in matches:
                # Add the part before the placeholder
                if match.start() > last_end:
                    self.format_parts.append(format_string[last_end : match.start()])

                # Add the placeholder
                self.format_parts.append(format_string[match.start() : match.end()])

                last_end = match.end()

            # Add the part after the last placeholder
            if last_end < len(format_string):
                self.format_parts.append(format_string[last_end:])

            # Add the arguments
            self.args.extend(args)

            # Add the named arguments
            self.named_args.update(kwargs)

            return self

        def add_statement(self, format_string: str, *args, **kwargs) -> "CodeBlock.Builder":
            parts = format_string.split("\n")
            single_line = len(parts) == 1
            if not single_line:
                statement = f"{parts[0]}\n$2>{'\n'.join(part for part in parts[1:])};\n$2<"
                self.add(statement, *args, **kwargs)
            else:
                self.add(format_string, *args, **kwargs)
                self.add(";\n")
            return self

        def add_line(self, format_string: str, *args, **kwargs) -> "CodeBlock.Builder":
            self.add(format_string, *args, **kwargs)
            self.add("\n")
            return self

        def begin_statement(self, format_string: str, *args, **kwargs) -> "CodeBlock.Builder":
            parts = format_string.split("\n")
            nested_items = parts[1:]
            statement = f"{parts[0]}$2>{'\n'.join(part for part in parts[1:])}"
            self.__statement_builder_lines = 1 + len(nested_items)
            self.add(statement, *args, **kwargs)
            return self

        def add_statement_item(self, format_string: str, *args, **kwargs) -> "CodeBlock.Builder":
            self.add("\n")
            self.add(format_string, *args, **kwargs)
            self.__statement_builder_lines += 1
            return self

        def end_statement(self) -> "CodeBlock.Builder":
            should_dedent_str = "$2<" if self.__statement_builder_lines > 1 else ""
            self.add(f";\n{should_dedent_str}")
            self.__statement_builder_lines = 0
            return self

        def add_comment(self, comment: str) -> "CodeBlock.Builder":
            self.add("// $L\n", comment)
            return self

        def begin_control_flow(self, control_flow_string: str, *args, **kwargs) -> "CodeBlock.Builder":
            self.add(control_flow_string, *args, **kwargs)
            self.add(" {\n$>")
            return self

        def next_control_flow(self, control_flow_string: str, *args, **kwargs) -> "CodeBlock.Builder":
            self.add("$<} ")
            self.add(control_flow_string, *args, **kwargs)
            self.add(" {\n$>")
            return self

        def end_control_flow(self) -> "CodeBlock.Builder":
            self.add("$<}\n")
            return self

        def build(self) -> "CodeBlock":
            if self.__statement_builder_lines != 0:
                raise ValueError("Started a statement but never ended")

            return CodeBlock(deep_copy(self.format_parts), deep_copy(self.args), deep_copy(self.named_args))
