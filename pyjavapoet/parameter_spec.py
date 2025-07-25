"""
ParameterSpec for representing method and constructor parameters.

This module defines the ParameterSpec class, which is used to represent
parameters for methods and constructors in Java.
"""

from typing import List, Set, Union

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import TypeName


class ParameterSpec:
    """
    Represents a parameter for a method or constructor.

    ParameterSpec instances are immutable. Use the builder to create new instances.
    """

    def __init__(
        self,
        type_name: "TypeName",
        name: str,
        modifiers: Set[Modifier],
        annotations: List["AnnotationSpec"],
        varargs: bool = False,
    ):
        self.type_name = type_name
        self.name = name
        self.modifiers = modifiers
        self.annotations = annotations
        self.varargs = varargs

    def emit(self, code_writer) -> None:
        # Emit annotations
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit(" ")

        # Emit modifiers
        for modifier in sorted(self.modifiers, key=lambda m: m.value):
            code_writer.emit(modifier.value)
            code_writer.emit(" ")

        # Emit type
        if self.varargs:
            # For varargs, emit the component type, not the array type
            from pyjavapoet.type_name import ArrayTypeName

            if isinstance(self.type_name, ArrayTypeName):
                self.type_name.component_type.emit(code_writer)
                code_writer.emit("...")
            else:
                self.type_name.emit(code_writer)
                code_writer.emit("...")
        else:
            self.type_name.emit(code_writer)

        # Emit name
        code_writer.emit(" ")
        code_writer.emit(self.name)

    def __str__(self) -> str:
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)
    
    def to_builder(self) -> "ParameterSpec.Builder":
        ...

    def copy(self) -> "ParameterSpec":
        return ParameterSpec(
            self.type_name.copy(),
            self.name,
            self.modifiers.copy(),
            [a.copy() for a in self.annotations],
            self.varargs,
        )

    @staticmethod
    def builder(type_name: Union["TypeName", str, type], name: str) -> "Builder":
        if not isinstance(type_name, TypeName):
            type_name = TypeName.get(type_name)
        return ParameterSpec.Builder(type_name, name)

    class Builder:
        """
        Builder for ParameterSpec instances.
        """

        def __init__(self, type_name: "TypeName", name: str):
            self.type_name = type_name
            self.name = name
            self.modifiers = set()
            self.annotations = []
            self.varargs = False

        def add_modifiers(self, *modifiers: Modifier) -> "ParameterSpec.Builder":
            self.modifiers.update(modifiers)
            return self

        def add_annotation(self, annotation_spec: "AnnotationSpec") -> "ParameterSpec.Builder":
            self.annotations.append(annotation_spec)
            return self

        def set_varargs(self, varargs: bool = True) -> "ParameterSpec.Builder":
            self.varargs = varargs
            return self

        def build(self) -> "ParameterSpec":
            return ParameterSpec(
                self.type_name, self.name, self.modifiers.copy(), self.annotations.copy(), self.varargs
            )
