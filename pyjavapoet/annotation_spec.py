"""
AnnotationSpec for representing Java annotations.

This module defines the AnnotationSpec class, which is used to represent
Java annotations for classes, methods, fields, parameters, etc.
"""

from typing import TYPE_CHECKING, Union

from pyjavapoet.code_block import CodeBlock

if TYPE_CHECKING:
    from pyjavapoet.code_writer import CodeWriter
    from pyjavapoet.type_name import TypeName


# Late import to avoid circular dependency
def _get_type_name_class():
    """Get TypeName class via late import to avoid circular dependency."""
    from pyjavapoet.type_name import TypeName

    return TypeName


class AnnotationSpec:
    """
    Represents a Java annotation.

    AnnotationSpec instances are immutable. Use the builder to create new instances.
    """

    def __init__(self, type_name: "TypeName", members: dict[str, list[CodeBlock]]):
        """
        Initialize a new AnnotationSpec.

        Args:
            type_name: The annotation type
            members: The annotation members (property name -> value)
        """
        self.type_name = type_name
        self.members = members

    def emit(self, code_writer: "CodeWriter") -> None:
        """
        Emit this annotation to a CodeWriter.

        Args:
            code_writer: The CodeWriter to emit to
        """
        code_writer.emit("@")
        self.type_name.emit(code_writer)

        if not self.members:
            return

        code_writer.emit("(")

        # For single member annotations with property "value", we can omit the property name
        if len(self.members) == 1 and "value" in self.members:
            for value in self.members["value"]:
                value.emit(code_writer)
        else:
            first = True
            for name, values in self.members.items():
                if not first:
                    code_writer.emit(", ")
                first = False

                code_writer.emit(name)
                code_writer.emit(" = ")

                # Handle array values
                if len(values) > 1:
                    code_writer.emit("{")
                    for i, value in enumerate(values):
                        if i > 0:
                            code_writer.emit(", ")
                        value.emit(code_writer)
                    code_writer.emit("}")
                else:
                    # Single value
                    values[0].emit(code_writer)

        code_writer.emit(")")

    def __str__(self) -> str:
        """
        Get a string representation of this annotation.

        Returns:
            A string representation
        """
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)
    
    def __hash__(self) -> int:
        return hash(str(self))

    @staticmethod
    def get(type_name: Union["TypeName", str, type]) -> "AnnotationSpec":
        """
        Create a simple annotation with no members.

        Args:
            type_name: The annotation type

        Returns:
            A new AnnotationSpec
        """
        return AnnotationSpec.builder(type_name).build()

    @staticmethod
    def builder(type_name: Union["TypeName", str, type]) -> "Builder":
        """
        Create a new AnnotationSpec builder.

        Args:
            type_name: The annotation type

        Returns:
            A new Builder
        """
        TypeName = _get_type_name_class()
        if not isinstance(type_name, TypeName):
            type_name = TypeName.get(type_name)
        return AnnotationSpec.Builder(type_name)

    class Builder:
        """
        Builder for AnnotationSpec instances.
        """

        def __init__(self, type_name: "TypeName"):
            """
            Initialize a new Builder.

            Args:
                type_name: The annotation type
            """
            self.type_name = type_name
            self.members: dict[str, list[CodeBlock]] = {}  # property name -> list of values

        def add_member(self, name: str, format_string: str, *args) -> "AnnotationSpec.Builder":
            """
            Add a member to the annotation.

            Args:
                name: The member name
                format_string: The format string for the value
                *args: The arguments to format with

            Returns:
                self for chaining
            """
            from pyjavapoet.code_block import CodeBlock

            code_block = CodeBlock.of(format_string, *args)

            if name not in self.members:
                self.members[name] = []

            self.members[name].append(code_block)
            return self

        def build(self) -> "AnnotationSpec":
            """
            Build a new AnnotationSpec.

            Returns:
                A new AnnotationSpec
            """
            # Create a deep copy of members
            members_copy = {}
            for name, values in self.members.items():
                members_copy[name] = values.copy()

            return AnnotationSpec(self.type_name, members_copy)
