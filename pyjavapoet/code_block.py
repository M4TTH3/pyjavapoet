"""
CodeBlock for formatting Java code with placeholders.

This module defines the CodeBlock class, which is a key component for
generating code with proper formatting and handling various types of
placeholders like $L (literals), $S (strings), $T (types), and $N (names).
"""

import re
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from pyjavapoet.code_writer import CodeWriter


class CodeBlock:
    """
    A fragment of code with formatting.

    CodeBlock instances are immutable. Use the builder to create new instances.
    """

    def __init__(self, format_parts: List[str], args: List[Any]):
        """
        Initialize a new CodeBlock.

        Args:
            format_parts: The format string parts
            args: The arguments to format with
        """
        self.format_parts = format_parts
        self.args = args

    def emit(self, code_writer: "CodeWriter") -> None:
        """
        Emit this code block to a CodeWriter.

        Args:
            code_writer: The CodeWriter to emit to
        """
        arg_index = 0

        for part in self.format_parts:
            # Look for placeholders like $L, $S, $T, $N
            placeholder_match = re.search(r"\$([LSTN])", part)
            if placeholder_match:
                # Emit everything before the placeholder
                if placeholder_match.start() > 0:
                    code_writer.emit(part[: placeholder_match.start()])

                # Get the placeholder type
                placeholder_type = placeholder_match.group(1)

                # Handle the placeholder
                if arg_index < len(self.args):
                    arg = self.args[arg_index]
                    arg_index += 1

                    if placeholder_type == "L":  # Literal
                        if isinstance(arg, CodeBlock):
                            arg.emit(code_writer)
                        else:
                            code_writer.emit(str(arg))

                    elif placeholder_type == "S":  # String
                        # Escape special characters
                        escaped = str(arg).replace("\\", "\\\\").replace('"', '\\"')

                        # Add quotes
                        code_writer.emit(f'"{escaped}"')

                    elif placeholder_type == "T":  # Type
                        # Let the CodeWriter handle type imports
                        code_writer.emit_type(arg)

                    elif placeholder_type == "N":  # Name
                        if hasattr(arg, "name"):
                            code_writer.emit(arg.name)
                        else:
                            code_writer.emit(str(arg))

                # Emit everything after the placeholder
                if placeholder_match.end() < len(part):
                    code_writer.emit(part[placeholder_match.end() :])
            else:
                # No placeholders, emit the whole part
                code_writer.emit(part)

    def __str__(self) -> str:
        """
        Get a string representation of this code block.

        Returns:
            A string representation
        """
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)

    @staticmethod
    def of(format_string: str, *args) -> "CodeBlock":
        """
        Create a CodeBlock from a format string and arguments.

        Args:
            format_string: The format string
            *args: The arguments to format with

        Returns:
            A new CodeBlock
        """
        return CodeBlock.builder().add(format_string, *args).build()

    @staticmethod
    def builder() -> "Builder":
        """
        Create a new CodeBlock builder.

        Returns:
            A new Builder
        """
        return CodeBlock.Builder()

    @staticmethod
    def join_to_code(code_blocks: List["CodeBlock"], separator: str) -> "CodeBlock":
        """
        Join multiple CodeBlocks with a separator.

        Args:
            code_blocks: The CodeBlocks to join
            separator: The separator to use

        Returns:
            A new CodeBlock
        """
        if not code_blocks:
            return CodeBlock([], [])

        builder = CodeBlock.builder()
        first = True

        for code_block in code_blocks:
            if not first:
                builder.add(separator)
            first = False

            builder.add("$L", code_block)

        return builder.build()

    class Builder:
        """
        Builder for CodeBlock instances.
        """

        def __init__(self):
            """
            Initialize a new Builder.
            """
            self.format_parts = []
            self.args = []

        def add(self, format_string: str, *args) -> "CodeBlock.Builder":
            """
            Add a format string and arguments.

            Args:
                format_string: The format string
                *args: The arguments to format with

            Returns:
                self for chaining
            """
            # Check for arguments in the format string
            pattern = r"\$([LSTN])"
            matches = list(re.finditer(pattern, format_string))

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

            return self

        def add_statement(self, format_string: str, *args) -> "CodeBlock.Builder":
            """
            Add a statement with arguments.

            Args:
                format_string: The format string
                *args: The arguments to format with

            Returns:
                self for chaining
            """
            self.add(format_string, *args)
            self.add(";\n")
            return self

        def begin_control_flow(self, control_flow_string: str, *args) -> "CodeBlock.Builder":
            """
            Begin a control flow statement.

            Args:
                control_flow_string: The control flow string (e.g., "if ($L)")
                *args: The arguments to format with

            Returns:
                self for chaining
            """
            self.add(control_flow_string, *args)
            self.add(" {\n")
            return self

        def next_control_flow(self, control_flow_string: str, *args) -> "CodeBlock.Builder":
            """
            Continue a control flow statement.

            Args:
                control_flow_string: The control flow string (e.g., "else if ($L)")
                *args: The arguments to format with

            Returns:
                self for chaining
            """
            self.add("} ")
            self.add(control_flow_string, *args)
            self.add(" {\n")
            return self

        def end_control_flow(self) -> "CodeBlock.Builder":
            """
            End a control flow statement.

            Returns:
                self for chaining
            """
            self.add("}\n")
            return self

        def build(self) -> "CodeBlock":
            """
            Build a new CodeBlock.

            Returns:
                A new CodeBlock
            """
            return CodeBlock(self.format_parts.copy(), self.args.copy())
