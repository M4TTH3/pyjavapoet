"""
MethodSpec for representing methods and constructors in Java classes.

This module defines the MethodSpec class, which is used to represent
methods and constructors in Java classes and interfaces.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING, List, Optional, Set, Union

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.modifier import Modifier
from pyjavapoet.parameter_spec import ParameterSpec
from pyjavapoet.type_name import TypeName, TypeVariableName

if TYPE_CHECKING:
    from pyjavapoet.code_writer import CodeWriter


class MethodSpec:
    """
    Represents a method or constructor in a class or interface.

    MethodSpec instances are immutable. Use the builder to create new instances.
    """

    class Kind(Enum):
        """
        Kind of method (normal method, constructor, or compact constructor).
        """

        METHOD = auto()
        CONSTRUCTOR = auto()
        COMPACT_CONSTRUCTOR = auto()

    def __init__(
        self,
        name: str,
        modifiers: Set[Modifier],
        parameters: List["ParameterSpec"],
        return_type: Optional["TypeName"],
        exceptions: List["TypeName"],
        type_variables: List["TypeVariableName"],
        javadoc: Optional["CodeBlock"],
        annotations: List["AnnotationSpec"],
        code: Optional["CodeBlock"],
        default_value: Optional["CodeBlock"],
        kind: "MethodSpec.Kind",
    ):
        self.name = name
        self.modifiers = modifiers
        self.parameters = parameters
        self.return_type = return_type
        self.exceptions = exceptions
        self.type_variables = type_variables
        self.javadoc = javadoc
        self.annotations = annotations
        self.code = code
        self.default_value = default_value
        self.kind = kind

        # Validate that constructors don't have a return type
        if self.kind == MethodSpec.Kind.CONSTRUCTOR and self.return_type is not None:
            raise ValueError("Constructors cannot have a return type")

    def emit(self, code_writer: "CodeWriter") -> None:
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

        # Emit type variables
        if self.type_variables:
            code_writer.emit("<")
            for i, type_variable in enumerate(self.type_variables):
                if i > 0:
                    code_writer.emit(", ")
                type_variable.emit(code_writer)
            code_writer.emit("> ")

        # Emit return type for methods
        if self.kind == MethodSpec.Kind.METHOD:
            if self.return_type is None:
                code_writer.emit("void")
            else:
                self.return_type.emit(code_writer)
            code_writer.emit(" ")

        # Emit name
        code_writer.emit(self.name)

        # Emit parameters
        code_writer.emit("(")
        for i, parameter in enumerate(self.parameters):
            if i > 0:
                code_writer.emit(", ")
            parameter.emit(code_writer)
        code_writer.emit(")")

        # Emit exceptions
        if self.exceptions:
            code_writer.emit(" throws ")
            for i, exception in enumerate(self.exceptions):
                if i > 0:
                    code_writer.emit(", ")
                exception.emit(code_writer)

        # Emit body or semicolon
        if Modifier.ABSTRACT in self.modifiers or (Modifier.NATIVE in self.modifiers and not self.default_value):
            code_writer.emit(";\n")
        elif self.default_value is not None:
            code_writer.emit(" default ")
            self.default_value.emit(code_writer)
            code_writer.emit(";\n")
        else:
            code_writer.emit(" {\n")
            code_writer.indent()

            if self.code is not None:
                self.code.emit(code_writer)

            code_writer.unindent()
            code_writer.emit("}\n")

    def __str__(self) -> str:
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)

    @staticmethod
    def method_builder(name: str) -> "Builder":
        return MethodSpec.Builder(name, MethodSpec.Kind.METHOD)

    @staticmethod
    def constructor_builder() -> "Builder":
        return MethodSpec.Builder("", MethodSpec.Kind.CONSTRUCTOR)

    @staticmethod
    def compact_constructor_builder() -> "Builder":
        return MethodSpec.Builder("", MethodSpec.Kind.COMPACT_CONSTRUCTOR)

    class Builder:
        """
        Builder for MethodSpec instances.
        """

        def __init__(self, name: str, kind: "MethodSpec.Kind"):
            self.name = name
            self.kind = kind
            self.modifiers = set()
            self.parameters = []
            self.return_type = None
            self.exceptions = []
            self.type_variables = []
            self.javadoc = None
            self.annotations = []
            self.code_builder = CodeBlock.builder() if kind != MethodSpec.Kind.COMPACT_CONSTRUCTOR else None
            self.default_value = None

        def add_modifiers(self, *modifiers: Modifier) -> "MethodSpec.Builder":
            self.modifiers.update(modifiers)
            # Check if modifiers are valid for methods
            Modifier.check_method_modifiers(self.modifiers)
            return self

        def add_parameter(
            self, type_name: Union["TypeName", str, type], name: str, *modifiers: Modifier
        ) -> "MethodSpec.Builder":
            parameter = ParameterSpec.builder(type_name, name)
            if modifiers:
                parameter.add_modifiers(*modifiers)
            self.parameters.append(parameter.build())
            return self

        def add_parameter_spec(self, parameter_spec: "ParameterSpec") -> "MethodSpec.Builder":
            self.parameters.append(parameter_spec)
            return self

        def returns(self, return_type: Union["TypeName", str, type]) -> "MethodSpec.Builder":
            if self.kind != MethodSpec.Kind.METHOD:
                raise ValueError("Only methods can have a return type")

            if not isinstance(return_type, TypeName):
                return_type = TypeName.get(return_type)

            self.return_type = return_type
            return self

        def add_exception(self, exception: Union["TypeName", str, type]) -> "MethodSpec.Builder":
            if not isinstance(exception, TypeName):
                exception = TypeName.get(exception)

            self.exceptions.append(exception)
            return self

        def add_type_variable(self, type_variable: "TypeVariableName") -> "MethodSpec.Builder":
            self.type_variables.append(type_variable)
            return self

        def add_javadoc(self, format_string: str, *args) -> "MethodSpec.Builder":
            self.javadoc = CodeBlock.of(format_string, *args)
            return self

        def add_annotation(self, annotation_spec: "AnnotationSpec") -> "MethodSpec.Builder":
            self.annotations.append(annotation_spec)
            return self

        def add_code(self, format_string: str, *args) -> "MethodSpec.Builder":
            if self.kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            self.code_builder.add(format_string, *args)
            return self

        def add_statement(self, format_string: str, *args) -> "MethodSpec.Builder":
            if self.kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            self.code_builder.add_statement(format_string, *args)
            return self

        def begin_control_flow(self, control_flow_string: str, *args) -> "MethodSpec.Builder":
            if self.kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            self.code_builder.begin_control_flow(control_flow_string, *args)
            return self

        def next_control_flow(self, control_flow_string: str, *args) -> "MethodSpec.Builder":
            if self.kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            self.code_builder.next_control_flow(control_flow_string, *args)
            return self

        def end_control_flow(self) -> "MethodSpec.Builder":
            if self.kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            self.code_builder.end_control_flow()
            return self

        def default_value(self, format_string: str, *args) -> "MethodSpec.Builder":
            self.default_value = CodeBlock.of(format_string, *args)
            return self

        def build(self) -> "MethodSpec":
            # Set constructor name from enclosing class
            if self.kind == MethodSpec.Kind.CONSTRUCTOR or self.kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                if not self.name:
                    # Will be set later when the method is added to a class
                    pass

            # Validate method
            if self.kind == MethodSpec.Kind.METHOD:
                if Modifier.ABSTRACT in self.modifiers and self.code_builder and self.code_builder.format_parts:
                    raise ValueError("Abstract methods cannot have a body")

            return MethodSpec(
                self.name,
                self.modifiers.copy(),
                self.parameters.copy(),
                self.return_type,
                self.exceptions.copy(),
                self.type_variables.copy(),
                self.javadoc,
                self.annotations.copy(),
                self.code_builder.build() if self.code_builder else None,
                self.default_value,
                self.kind,
            )
