"""
ParameterSpec for representing method and constructor parameters.

This module defines the ParameterSpec class, which is used to represent
parameters for methods and constructors in Java.
"""

import re
from typing import TYPE_CHECKING, List, Set, Union

from code_base import Code
from util import deep_copy, throw_if_invalid_java_identifier

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ArrayTypeName, TypeName

if TYPE_CHECKING:
    from pyjavapoet.code_writer import CodeWriter


class ParameterSpec(Code["ParameterSpec"]):
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

    def emit(self, code_writer: "CodeWriter") -> None:
        # Emit annotations
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit(" ")

        # Emit modifiers
        for modifier in Modifier.ordered_modifiers(self.modifiers):
            code_writer.emit(modifier.value)
            code_writer.emit(" ")

        # Emit type
        if self.varargs:
            # For varargs, emit the component type, not the array type
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
    
    def to_builder(self) -> "ParameterSpec.Builder":
        return ParameterSpec.Builder(self.type_name, self.name, self.modifiers, self.annotations, self.varargs)

    @staticmethod
    def builder(type_name: Union["TypeName", str, type], name: str) -> "Builder":
        receiver_pattern = r"^(?:[A-Za-z_][A-Za-z0-9_]*\.)?this$"
        if not re.match(receiver_pattern, name):
            throw_if_invalid_java_identifier(name)

        if not isinstance(type_name, TypeName):
            type_name = TypeName.get(type_name)
        return ParameterSpec.Builder(type_name, name)

    class Builder(Code.Builder["ParameterSpec"]):
        """
        Builder for ParameterSpec instances.
        """

        def __init__(
            self,
            type_name: "TypeName",
            name: str,
            modifiers: Set[Modifier] | None = None,
            annotations: List["AnnotationSpec"] | None = None,
            varargs: bool = False,
        ):
            self.type_name = type_name
            self.name = name
            self.modifiers = modifiers or set()
            self.annotations = annotations or []
            self.varargs = varargs

        def add_final(self) -> "ParameterSpec.Builder":
            self.modifiers.add(Modifier.FINAL)
            return self

        def add_annotation(self, annotation_spec: "AnnotationSpec") -> "ParameterSpec.Builder":
            self.annotations.append(annotation_spec)
            return self

        def set_varargs(self, varargs: bool = True) -> "ParameterSpec.Builder":
            self.varargs = varargs
            return self

        def build(self) -> "ParameterSpec":
            return ParameterSpec(
                deep_copy(self.type_name),
                self.name,
                deep_copy(self.modifiers),
                deep_copy(self.annotations),
                self.varargs,
            )
