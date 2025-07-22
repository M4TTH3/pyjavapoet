"""
FieldSpec for representing fields in Java classes and interfaces.

This module defines the FieldSpec class, which is used to represent
fields in Java classes, interfaces, and enums.
"""

from typing import TYPE_CHECKING, Optional, Union

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import TypeName

if TYPE_CHECKING:
    from pyjavapoet.code_writer import CodeWriter


class FieldSpec:
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
        if self.javadoc is not None:
            code_writer.emit("/**\n")
            code_writer.emit(" * ")
            self.javadoc.emit(code_writer)
            code_writer.emit("*/\n")

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

    def __str__(self) -> str:
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FieldSpec):
            return False
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))
    
    def to_builder(self) -> "Builder":
        return FieldSpec.Builder(
            self.type_name.copy(),
            self.name,
            self.modifiers.copy(),
            self.annotations.copy(),
            self.javadoc.copy() if self.javadoc is not None else None,
            self.initializer.copy() if self.initializer is not None else None,
        )

    @staticmethod
    def is_valid_field_name(name: str) -> bool:
        java_keywords = {
            "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const",
            "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float",
            "for", "goto", "if", "implements", "import", "instanceof", "int", "interface", "long", "native",
            "new", "package", "private", "protected", "public", "return", "short", "static", "strictfp",
            "super", "switch", "synchronized", "this", "throw", "throws", "transient", "try", "void",
            "volatile", "while", "true", "false", "null"
        }
        return name.isidentifier() and name not in java_keywords

    @staticmethod
    def builder(type_name: Union["TypeName", str, type], name: str) -> "Builder":
        if not FieldSpec.is_valid_field_name(name):
            raise ValueError(f"Invalid field name: {name}")

        if not isinstance(type_name, TypeName):
            type_name = TypeName.get(type_name)
        return FieldSpec.Builder(type_name, name)

    class Builder:
        """
        Builder for FieldSpec instances.
        """

        __type_name: "TypeName"
        __name: str
        __modifiers: set[Modifier]
        __annotations: list["AnnotationSpec"]
        __javadoc: Optional["CodeBlock"]
        __initializer: Optional["CodeBlock"]

        def __init__(self, 
            type_name: "TypeName", 
            name: str, 
            modifiers: set[Modifier] = set(), 
            annotations: list["AnnotationSpec"] = [], 
            javadoc: Optional["CodeBlock"] = None, 
            initializer: Optional["CodeBlock"] = None
        ):
            self.__type_name = type_name
            self.__name = name
            self.__modifiers = modifiers
            self.__annotations = annotations
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

        def set_javadoc(self, format_string: str, *args) -> "FieldSpec.Builder":
            self.__javadoc = CodeBlock.of(format_string, *args)
            return self

        def initializer(self, format_string: str, *args) -> "FieldSpec.Builder":
            self.__initializer = CodeBlock.of(format_string, *args)
            return self

        def build(self) -> "FieldSpec":
            return FieldSpec(
                self.__type_name,
                self.__name,
                self.__modifiers.copy(),
                self.__annotations.copy(),
                self.__javadoc,
                self.__initializer,
            )
