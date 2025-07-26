"""
FieldSpec for representing fields in Java classes and interfaces.

This module defines the FieldSpec class, which is used to represent
fields in Java classes, interfaces, and enums.
"""

from typing import TYPE_CHECKING, Optional, Union

from code_base import Code
from util import deep_copy

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import TypeName

if TYPE_CHECKING:
    from pyjavapoet.code_writer import CodeWriter


class FieldSpec(Code["FieldSpec"]):
    """
    Represents a field in a class, interface, or enum.

    FieldSpec instances are immutable. Use the builder to create new instances.
    """

    def __init__(
        self,
        type_name: "TypeName",
        name: str,
        modifiers: set[Modifier],
        annotations: list["AnnotationSpec"],
        javadoc: Optional["CodeBlock"],
        initializer: Optional["CodeBlock"],
    ):
        self.type_name = type_name
        self.name = name
        self.modifiers = modifiers
        self.annotations = annotations
        self.javadoc = javadoc
        self.initializer = initializer

    def emit(self, code_writer: "CodeWriter") -> None:
        # Emit Javadoc
        if self.javadoc:
            self.javadoc.emit_javadoc(code_writer)
            code_writer.emit("\n")

        # Emit annotations
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit("\n")

        # Emit modifiers
        for modifier in Modifier.ordered_modifiers(self.modifiers):
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

    def to_builder(self) -> "Builder":
        return FieldSpec.Builder(
            deep_copy(self.type_name),
            self.name,
            deep_copy(self.modifiers),
            deep_copy(self.annotations),
            deep_copy(self.javadoc),
            deep_copy(self.initializer),
        )

    @staticmethod
    def is_valid_field_name(name: str) -> bool:
        java_keywords = {
            "abstract",
            "assert",
            "boolean",
            "break",
            "byte",
            "case",
            "catch",
            "char",
            "class",
            "const",
            "continue",
            "default",
            "do",
            "double",
            "else",
            "enum",
            "extends",
            "final",
            "finally",
            "float",
            "for",
            "goto",
            "if",
            "implements",
            "import",
            "instanceof",
            "int",
            "interface",
            "long",
            "native",
            "new",
            "package",
            "private",
            "protected",
            "public",
            "return",
            "short",
            "static",
            "strictfp",
            "super",
            "switch",
            "synchronized",
            "this",
            "throw",
            "throws",
            "transient",
            "try",
            "void",
            "volatile",
            "while",
            "true",
            "false",
            "null",
        }
        return name.isidentifier() and name not in java_keywords

    @staticmethod
    def builder(type_name: Union["TypeName", str, type], name: str) -> "Builder":
        if not FieldSpec.is_valid_field_name(name):
            raise ValueError(f"Invalid field name: {name}")

        if not isinstance(type_name, TypeName):
            type_name = TypeName.get(type_name)
        return FieldSpec.Builder(type_name, name)

    class Builder(Code.Builder["FieldSpec"]):
        """
        Builder for FieldSpec instances.
        """

        __type_name: "TypeName"
        __name: str
        __modifiers: set[Modifier]
        __annotations: list["AnnotationSpec"]
        __javadoc: Optional["CodeBlock"]
        __initializer: Optional["CodeBlock"]

        def __init__(
            self,
            type_name: "TypeName",
            name: str,
            modifiers: set[Modifier] | None = None,
            annotations: list["AnnotationSpec"] | None = None,
            javadoc: Optional["CodeBlock"] = None,
            initializer: Optional["CodeBlock"] = None,
        ):
            self.__type_name = type_name
            self.__name = name
            self.__modifiers = modifiers or set()
            self.__annotations = annotations or []
            self.__javadoc = javadoc
            self.__initializer = initializer

        def add_modifiers(self, *modifiers: Modifier) -> "FieldSpec.Builder":
            self.__modifiers.update(modifiers)
            # Check if modifiers are valid for fields
            Modifier.check_field_modifiers(self.__modifiers)
            return self

        def add_annotation(self, annotation_spec: "AnnotationSpec") -> "FieldSpec.Builder":
            self.__annotations.append(annotation_spec)
            return self

        def add_javadoc(self, format_string: str, *args) -> "FieldSpec.Builder":
            self.__javadoc = CodeBlock.add_javadoc(self.__javadoc, format_string, *args)
            return self

        def initializer(self, format_string: str | CodeBlock, *args) -> "FieldSpec.Builder":
            if isinstance(format_string, str):
                self.__initializer = CodeBlock.of(format_string, *args)
            else:
                self.__initializer = format_string
            return self

        def build(self) -> "FieldSpec":
            return FieldSpec(
                deep_copy(self.__type_name),
                self.__name,
                deep_copy(self.__modifiers),
                deep_copy(self.__annotations),
                deep_copy(self.__javadoc),
                deep_copy(self.__initializer),
            )
