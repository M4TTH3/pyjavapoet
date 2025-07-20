"""
FieldSpec for representing fields in Java classes and interfaces.

This module defines the FieldSpec class, which is used to represent
fields in Java classes, interfaces, and enums.
"""

from typing import List, Optional, Set, Union

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import TypeName


class FieldSpec:
    """
    Represents a field in a class, interface, or enum.

    FieldSpec instances are immutable. Use the builder to create new instances.
    """

    def __init__(
        self,
        type_name: "TypeName",
        name: str,
        modifiers: Set[Modifier],
        annotations: List["AnnotationSpec"],
        javadoc: Optional["CodeBlock"],
        initializer: Optional["CodeBlock"],
    ):
        """
        Initialize a new FieldSpec.

        Args:
            type_name: The field type
            name: The field name
            modifiers: The field modifiers
            annotations: The field annotations
            javadoc: The field Javadoc
            initializer: The field initializer
        """
        self.type_name = type_name
        self.name = name
        self.modifiers = modifiers
        self.annotations = annotations
        self.javadoc = javadoc
        self.initializer = initializer

    def emit(self, code_writer) -> None:
        """
        Emit this field to a CodeWriter.

        Args:
            code_writer: The CodeWriter to emit to
        """
        # Emit Javadoc
        if self.javadoc is not None:
            code_writer.emit("/**\n")
            code_writer.emit(" * ")
            self.javadoc.emit(code_writer)
            code_writer.emit("\n */\n")

        # Emit annotations
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit("\n")

        # Emit modifiers
        for modifier in sorted(self.modifiers, key=lambda m: m.value):
            code_writer.emit(modifier.value)
            code_writer.emit(" ")

        # Emit type and name
        code_writer.emit_type(self.type_name)
        code_writer.emit(" ")
        code_writer.emit(self.name)

        # Emit initializer
        if self.initializer is not None:
            code_writer.emit(" = ")
            self.initializer.emit(code_writer)

        code_writer.emit(";\n")

    def __str__(self) -> str:
        """
        Get a string representation of this field.

        Returns:
            A string representation
        """
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)

    @staticmethod
    def builder(type_name: Union["TypeName", str, type], name: str) -> "Builder":
        """
        Create a new FieldSpec builder.

        Args:
            type_name: The field type
            name: The field name

        Returns:
            A new Builder
        """
        if not isinstance(type_name, TypeName):
            type_name = TypeName.get(type_name)
        return FieldSpec.Builder(type_name, name)

    class Builder:
        """
        Builder for FieldSpec instances.
        """

        def __init__(self, type_name: "TypeName", name: str):
            """
            Initialize a new Builder.

            Args:
                type_name: The field type
                name: The field name
            """
            self.type_name = type_name
            self.name = name
            self.modifiers = set()
            self.annotations = []
            self.javadoc = None
            self.initializer = None

        def add_modifiers(self, *modifiers: Modifier) -> "FieldSpec.Builder":
            """
            Add modifiers to the field.

            Args:
                *modifiers: The modifiers to add

            Returns:
                self for chaining
            """
            self.modifiers.update(modifiers)
            # Check if modifiers are valid for fields
            Modifier.check_field_modifiers(self.modifiers)
            return self

        def add_annotation(self, annotation_spec: "AnnotationSpec") -> "FieldSpec.Builder":
            """
            Add an annotation to the field.

            Args:
                annotation_spec: The annotation to add

            Returns:
                self for chaining
            """
            self.annotations.append(annotation_spec)
            return self

        def add_javadoc(self, format_string: str, *args) -> "FieldSpec.Builder":
            """
            Add Javadoc to the field.

            Args:
                format_string: The format string
                *args: The arguments to format with

            Returns:
                self for chaining
            """
            self.javadoc = CodeBlock.of(format_string, *args)
            return self

        def set_initializer(self, format_string: str, *args) -> "FieldSpec.Builder":
            """
            Set the initializer for the field.

            Args:
                format_string: The format string
                *args: The arguments to format with

            Returns:
                self for chaining
            """
            self.initializer = CodeBlock.of(format_string, *args)
            return self

        def build(self) -> "FieldSpec":
            """
            Build a new FieldSpec.

            Returns:
                A new FieldSpec
            """
            return FieldSpec(
                self.type_name,
                self.name,
                self.modifiers.copy(),
                self.annotations.copy(),
                self.javadoc,
                self.initializer,
            )
