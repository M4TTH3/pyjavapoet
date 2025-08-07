"""
Copyright (C) 2015 Square, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Modified by Matthew Au-Yeung on 2025-07-29; see changelog.md for more details.
- Similar APIs ported from Java to Python.
"""

from enum import Enum, auto
from typing import Optional, Union

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.code_base import Code
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.code_writer import EMPTY_STRING, CodeWriter
from pyjavapoet.modifier import Modifier
from pyjavapoet.parameter_spec import ParameterSpec
from pyjavapoet.type_name import TypeName, TypeVariableName
from pyjavapoet.util import deep_copy


class MethodSpec(Code["MethodSpec"]):
    """
    Represents a method or constructor in a class or interface. Includes modifiers, return type, parameters, and body.

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
        modifiers: set[Modifier],
        parameters: list["ParameterSpec"],
        return_type: Optional["TypeName"],
        exceptions: set["TypeName"],
        type_variables: list["TypeVariableName"],
        javadoc: Optional["CodeBlock"],
        annotations: list["AnnotationSpec"],
        code: Optional["CodeBlock"],
        default_value: Optional["CodeBlock"],
        kind: "MethodSpec.Kind",
        in_interface: bool,
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
        self.in_interface = in_interface
        # Validate that constructors don't have a return type
        if self.kind == MethodSpec.Kind.CONSTRUCTOR and self.return_type is not None:
            raise ValueError("Constructors cannot have a return type")

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
            if not self.return_type:
                code_writer.emit("void")
            elif isinstance(self.return_type, TypeVariableName):
                self.return_type.emit_name_only(code_writer)
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
            for i, exception in enumerate(sorted(self.exceptions, key=lambda x: str(x))):
                if i > 0:
                    code_writer.emit(", ")
                exception.emit(code_writer)

        # Emit body or semicolon
        if self.default_value:
            code_writer.emit(" default ")
            self.default_value.emit(code_writer)
            code_writer.emit(";\n")
        elif (
            Modifier.ABSTRACT in self.modifiers
            or Modifier.NATIVE in self.modifiers
            or (self.in_interface and Modifier.DEFAULT not in self.modifiers)
        ):
            code_writer.emit(";\n")
        else:
            code_writer.emit(" {\n")
            code_writer.indent()

            if self.code is not None:
                self.code.emit(code_writer)

            code_writer.unindent()
            code_writer.emit("}\n")

    def to_builder(self) -> "MethodSpec.Builder":
        return MethodSpec.Builder(
            self.name,
            self.kind,
            deep_copy(self.modifiers),
            deep_copy(self.parameters),
            deep_copy(self.return_type),
            deep_copy(self.exceptions),
            deep_copy(self.type_variables),
            deep_copy(self.javadoc),
            deep_copy(self.annotations),
            self.code.to_builder() if self.code else CodeBlock.builder(),
            deep_copy(self.default_value),
            self.in_interface,
        )

    @staticmethod
    def method_builder(name: str) -> "Builder":
        return MethodSpec.Builder(name, MethodSpec.Kind.METHOD)

    @staticmethod
    def constructor_builder() -> "Builder":
        return MethodSpec.Builder("<init>", MethodSpec.Kind.CONSTRUCTOR)

    @staticmethod
    def compact_constructor_builder() -> "Builder":
        return MethodSpec.Builder("", MethodSpec.Kind.COMPACT_CONSTRUCTOR)

    class Builder(Code.Builder["MethodSpec"]):
        """
        Builder for MethodSpec instances.
        """

        # Private fields defined at the top
        __name: str
        __kind: "MethodSpec.Kind"
        __modifiers: set[Modifier]
        __parameters: list["ParameterSpec"]
        __return_type: Optional["TypeName"]
        __exceptions: set["TypeName"]
        __type_variables: list["TypeVariableName"]
        __javadoc: Optional["CodeBlock"]
        __annotations: list["AnnotationSpec"]
        __code_builder: "CodeBlock.Builder"
        __default_value: Optional["CodeBlock"]
        __in_interface: bool

        def __init__(
            self,
            name: str,
            kind: "MethodSpec.Kind",
            modifiers: set[Modifier] | None = None,
            parameters: list["ParameterSpec"] | None = None,
            return_type: Optional["TypeName"] = None,
            exceptions: set["TypeName"] | None = None,
            type_variables: list["TypeVariableName"] | None = None,
            javadoc: Optional["CodeBlock"] = None,
            annotations: list["AnnotationSpec"] | None = None,
            code_builder: Optional["CodeBlock.Builder"] = None,
            default_value: Optional["CodeBlock"] = None,
            in_interface: bool = False,
        ):
            self.__name = name
            self.__kind = kind
            self.__modifiers = modifiers or set()
            self.__parameters = parameters or []
            self.__return_type = return_type
            self.__exceptions = exceptions or set()
            self.__type_variables = type_variables or []
            self.__javadoc = javadoc
            self.__annotations = annotations or []
            self.__code_builder = code_builder or CodeBlock.builder()
            self.__default_value = default_value
            self.__in_interface = in_interface

        def add_modifiers(self, *modifiers: Modifier) -> "MethodSpec.Builder":
            self.__modifiers.update(modifiers)
            # Check if modifiers are valid for methods
            Modifier.check_method_modifiers(self.__modifiers)
            return self

        def add_parameter(
            self,
            parameter_spec: Union["ParameterSpec", "TypeName", str, type],
            name: str,
            final: bool = False,
        ) -> "MethodSpec.Builder":
            if isinstance(parameter_spec, ParameterSpec):
                parameter = parameter_spec.to_builder()
            else:
                parameter = ParameterSpec.builder(parameter_spec, name)

            if final:
                parameter.add_final()
            self.__parameters.append(parameter.build())
            return self

        def add_parameter_spec(self, parameter_spec: "ParameterSpec") -> "MethodSpec.Builder":
            self.__parameters.append(parameter_spec)
            return self

        def returns(self, return_type: Union["TypeName", str, type]) -> "MethodSpec.Builder":
            if self.__kind != MethodSpec.Kind.METHOD:
                raise ValueError("Only methods can have a return type")

            if not isinstance(return_type, TypeName):
                return_type = TypeName.get(return_type)

            self.__return_type = return_type
            return self

        def add_exception(self, exception: Union["TypeName", str, type]) -> "MethodSpec.Builder":
            if not isinstance(exception, TypeName):
                exception = TypeName.get(exception)

            self.__exceptions.add(exception)
            return self

        def add_type_variable(self, type_variable: "TypeVariableName") -> "MethodSpec.Builder":
            self.__type_variables.append(type_variable)
            return self

        def add_javadoc(self, format_string: str, *args) -> "MethodSpec.Builder":
            self.__javadoc = CodeBlock.add_javadoc(self.__javadoc, format_string, *args)
            return self

        def add_javadoc_line(self, format_string: str = EMPTY_STRING, *args) -> "MethodSpec.Builder":
            self.__javadoc = CodeBlock.add_javadoc_line(self.__javadoc, format_string, *args)
            return self

        def add_annotation(self, annotation_spec: "AnnotationSpec") -> "MethodSpec.Builder":
            self.__annotations.append(annotation_spec)
            return self

        def add_raw_code(self, format_string: str, *args) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            if self.__code_builder is not None:
                self.__code_builder.add(format_string, *args)
            return self

        def add_raw_line(self, format_string: str, *args) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            if self.__code_builder is not None:
                self.__code_builder.add_line(format_string, *args)
            return self

        def add_statement(self, format_string: str, *args) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            if self.__code_builder is not None:
                self.__code_builder.add_statement(format_string, *args)
            return self

        def begin_statement_chain(self, format_string: str, *args) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            if self.__code_builder:
                self.__code_builder.begin_statement(format_string, *args)
            return self

        def add_chained_item(self, format_string: str, *args) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            if self.__code_builder:
                self.__code_builder.add_statement_item(format_string, *args)
            return self

        def end_statement_chain(self) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            if self.__code_builder:
                self.__code_builder.end_statement()
            return self

        def add_comment(self, comment: str) -> "MethodSpec.Builder":
            if self.__code_builder is not None:
                self.__code_builder.add_comment(comment)
            return self

        def begin_control_flow(self, control_flow_string: str, *args) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            if self.__code_builder is not None:
                self.__code_builder.begin_control_flow(control_flow_string, *args)
            return self

        def next_control_flow(self, control_flow_string: str, *args) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")

            if self.__code_builder is not None:
                self.__code_builder.next_control_flow(control_flow_string, *args)
            return self

        def end_control_flow(self) -> "MethodSpec.Builder":
            if self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                raise ValueError("Compact constructors cannot have a body")
            self.__code_builder.end_control_flow()
            return self

        def default_value(self, format_string: str, *args) -> "MethodSpec.Builder":
            self.__default_value = CodeBlock.of(format_string, *args)
            return self

        def in_interface(self) -> "MethodSpec.Builder":
            self.__in_interface = True
            return self

        def set_name(self, name: str) -> "MethodSpec.Builder":
            self.__name = name
            return self

        def build(self) -> "MethodSpec":
            # Set constructor name from enclosing class
            if self.__kind == MethodSpec.Kind.CONSTRUCTOR or self.__kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR:
                if not self.__name:
                    # Will be set later when the method is added to a class
                    pass

            # Validate method
            if self.__kind == MethodSpec.Kind.METHOD:
                if Modifier.ABSTRACT in self.__modifiers and self.__code_builder and self.__code_builder.format_parts:
                    raise ValueError("Abstract methods cannot have a body")

            return MethodSpec(
                self.__name,
                deep_copy(self.__modifiers),
                deep_copy(self.__parameters),
                deep_copy(self.__return_type),
                deep_copy(self.__exceptions),
                deep_copy(self.__type_variables),
                deep_copy(self.__javadoc),
                deep_copy(self.__annotations),
                self.__code_builder.build() if self.__code_builder else None,
                deep_copy(self.__default_value),
                deep_copy(self.__kind),
                self.__in_interface,
            )
