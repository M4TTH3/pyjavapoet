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
        """
        Initialize a new ParameterSpec.

        Args:
            type_name: The parameter type
            name: The parameter name
            modifiers: The parameter modifiers
            annotations: The parameter annotations
            varargs: Whether the parameter is a varargs parameter
        """
        self.type_name = type_name
        self.name = name
        self.modifiers = modifiers
        self.annotations = annotations
        self.varargs = varargs

    def emit(self, code_writer) -> None:
        """
        Emit this parameter to a CodeWriter.

        Args:
            code_writer: The CodeWriter to emit to
        """
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
        """
        Get a string representation of this parameter.

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
        Create a new ParameterSpec builder.

        Args:
            type_name: The parameter type
            name: The parameter name

        Returns:
            A new Builder
        """
        if not isinstance(type_name, TypeName):
            type_name = TypeName.get(type_name)
        return ParameterSpec.Builder(type_name, name)

    class Builder:
        """
        Builder for ParameterSpec instances.
        """

        def __init__(self, type_name: "TypeName", name: str):
            """
            Initialize a new Builder.

            Args:
                type_name: The parameter type
                name: The parameter name
            """
            self.type_name = type_name
            self.name = name
            self.modifiers = set()
            self.annotations = []
            self.varargs = False

        def add_modifiers(self, *modifiers: Modifier) -> "ParameterSpec.Builder":
            """
            Add modifiers to the parameter.

            Args:
                *modifiers: The modifiers to add

            Returns:
                self for chaining
            """
            self.modifiers.update(modifiers)
            return self

        def add_annotation(self, annotation_spec: "AnnotationSpec") -> "ParameterSpec.Builder":
            """
            Add an annotation to the parameter.

            Args:
                annotation_spec: The annotation to add

            Returns:
                self for chaining
            """
            self.annotations.append(annotation_spec)
            return self

        def set_varargs(self, varargs: bool = True) -> "ParameterSpec.Builder":
            """
            Set whether the parameter is a varargs parameter.

            Args:
                varargs: Whether the parameter is a varargs parameter

            Returns:
                self for chaining
            """
            self.varargs = varargs
            return self

        def build(self) -> "ParameterSpec":
            """
            Build a new ParameterSpec.

            Returns:
                A new ParameterSpec
            """
            return ParameterSpec(
                self.type_name, self.name, self.modifiers.copy(), self.annotations.copy(), self.varargs
            )
