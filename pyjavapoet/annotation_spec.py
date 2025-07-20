"""
AnnotationSpec for representing Java annotations.

This module defines the AnnotationSpec class, which is used to represent
Java annotations for classes, methods, fields, parameters, etc.
"""

from typing import Union

from pyjavapoet.code_block import CodeBlock
from pyjavapoet.code_writer import CodeWriter
from pyjavapoet.type_name import TypeName


class AnnotationSpec:
    """
    Represents a Java annotation.

    AnnotationSpec instances are immutable. Use the builder to create new instances.
    """

    def __init__(self, type_name: "TypeName", members: dict[str, list[CodeBlock]]):
        self.type_name = type_name
        self.members = members

    def emit(self, code_writer: "CodeWriter") -> None:
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
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)
    
    def __hash__(self) -> int:
        return hash(str(self))

    @staticmethod
    def get(type_name: Union["TypeName", str, type]) -> "AnnotationSpec":
        return AnnotationSpec.builder(type_name).build()

    @staticmethod
    def builder(type_name: Union["TypeName", str, type]) -> "Builder":
        return AnnotationSpec.Builder(TypeName.get(type_name))

    class Builder:
        """
        Builder for AnnotationSpec instances.
        """

        def __init__(self, type_name: "TypeName"):
            self.type_name = type_name
            self.members: dict[str, list[CodeBlock]] = {}  # property name -> list of values

        def add_member(self, name: str, format_string: str, *args) -> "AnnotationSpec.Builder":
            from pyjavapoet.code_block import CodeBlock

            code_block = CodeBlock.of(format_string, *args)

            if name not in self.members:
                self.members[name] = []

            self.members[name].append(code_block)
            return self

        def build(self) -> "AnnotationSpec":
            # Create a deep copy of members
            members_copy = {}
            for name, values in self.members.items():
                members_copy[name] = values.copy()

            return AnnotationSpec(self.type_name, members_copy)
