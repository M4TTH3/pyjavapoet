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
from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.parameter_spec import ParameterSpec
from pyjavapoet.type_name import ClassName, TypeName, TypeVariableName
from pyjavapoet.util import deep_copy


class TypeSpec(Code["TypeSpec"]):
    """
    Represents a class, interface, enum, annotation, or record declaration.

    TypeSpec instances are immutable. Use the builder to create new instances.
    """

    class Kind(Enum):
        """
        Kind of type (class, interface, enum, annotation, or record).
        """

        CLASS = auto()
        INTERFACE = auto()
        ENUM = auto()
        ANNOTATION = auto()
        RECORD = auto()

    # Fields for TypeSpec
    name: str
    kind: "TypeSpec.Kind"
    modifiers: set["Modifier"]
    type_variables: list["TypeVariableName"]
    superclass: "TypeName | None"
    superinterfaces: list["TypeName"]
    permitted_subclasses: list["TypeName"]
    javadoc: "CodeBlock | None"
    annotations: list["AnnotationSpec"]
    fields: list["FieldSpec"]
    methods: list["MethodSpec"]
    types: list["TypeSpec"]
    enum_constants: dict[str, "TypeSpec"]
    record_components: list[tuple["TypeName", str]]

    # For anonymous classes
    anonymous_class_format: str
    anonymous_class_args: list

    def __init__(
        self,
        name: str,
        kind: "TypeSpec.Kind",
        modifiers: set[Modifier],
        type_variables: list[TypeVariableName],
        superclass: Optional[TypeName],
        superinterfaces: list[TypeName],
        permitted_subclasses: list[TypeName],
        javadoc: Optional[CodeBlock],
        annotations: list[AnnotationSpec],
        fields: list[FieldSpec],
        methods: list[MethodSpec],
        types: list["TypeSpec"],
        enum_constants: dict[str, "TypeSpec"],
        record_components: list[tuple[TypeName, str]],
    ):
        self.name = name
        self.kind = kind
        self.modifiers = modifiers
        self.type_variables = type_variables
        self.superclass = superclass
        self.superinterfaces = superinterfaces
        self.permitted_subclasses = permitted_subclasses
        self.javadoc = javadoc
        self.annotations = annotations
        self.fields = fields
        self.methods = methods
        self.types = types
        self.enum_constants = enum_constants
        self.record_components = record_components

        # For anonymous classes
        self.anonymous_class_format = ""
        self.anonymous_class_args = []

    def emit(self, code_writer: "CodeWriter") -> None:
        # Check if this is an anonymous class
        is_anonymous = not self.name and self.superclass

        if is_anonymous:
            # Emit anonymous class: new TypeName() { ... }
            code_writer.emit("new ")
            if self.superclass:
                self.superclass.emit(code_writer)
            code_writer.emit("(")
            if self.anonymous_class_format:
                code_block = CodeBlock.of(self.anonymous_class_format, *self.anonymous_class_args)
                code_block.emit(code_writer)
            code_writer.emit(")")
            # Skip the rest of the emission for anonymous classes
            code_writer.emit(" {\n")
            code_writer.indent()

            # Emit fields
            for field in self.fields:
                field.emit(code_writer)

            if self.fields and self.methods:
                code_writer.emit("\n")

            # Emit methods
            for method in self.methods:
                method.emit(code_writer)
                code_writer.emit("\n")

            code_writer.unindent()
            code_writer.emit("}")
            return

        self.__exclude_direct_inner_classes(code_writer)

        # Emit regular class/interface/enum
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

        # Emit kind
        if self.kind == TypeSpec.Kind.CLASS:
            code_writer.emit("class")
        elif self.kind == TypeSpec.Kind.INTERFACE:
            code_writer.emit("interface")
        elif self.kind == TypeSpec.Kind.ENUM:
            code_writer.emit("enum")
        elif self.kind == TypeSpec.Kind.ANNOTATION:
            code_writer.emit("@interface")
        elif self.kind == TypeSpec.Kind.RECORD:
            code_writer.emit("record")

        # Emit name and type variables
        code_writer.emit(" ")
        code_writer.emit(self.name)

        if self.type_variables:
            code_writer.emit("<")
            for i, type_variable in enumerate(self.type_variables):
                if i > 0:
                    code_writer.emit(", ")
                type_variable.emit(code_writer)
            code_writer.emit(">")

        # Emit record components
        if self.kind == TypeSpec.Kind.RECORD:
            code_writer.emit("(")
            for i, (type_name, name) in enumerate(self.record_components):
                if i > 0:
                    code_writer.emit(", ")
                code_writer.emit_type(type_name)
                code_writer.emit(" ")
                code_writer.emit(name)
            code_writer.emit(")")

        # Emit superclass
        if self.superclass is not None and self.kind != TypeSpec.Kind.ENUM:
            code_writer.emit(" extends ")
            code_writer.emit_type(self.superclass)

        # Emit superinterfaces
        if self.superinterfaces:
            keyword = (
                " implements "
                if self.kind in (TypeSpec.Kind.CLASS, TypeSpec.Kind.RECORD, TypeSpec.Kind.ENUM)
                else " extends "
            )
            code_writer.emit(keyword)
            for i, superinterface in enumerate(self.superinterfaces):
                if i > 0:
                    code_writer.emit(", ")
                code_writer.emit_type(superinterface)

        # Emit permitted subclasses
        if self.permitted_subclasses:
            code_writer.emit(" permits ")
            for i, subclass in enumerate(self.permitted_subclasses):
                if i > 0:
                    code_writer.emit(", ")
                code_writer.emit_type(subclass)

        code_writer.emit(" {\n")
        code_writer.indent()

        # Emit enum constants
        if self.kind == TypeSpec.Kind.ENUM and self.enum_constants:
            for i, (name, constant) in enumerate(self.enum_constants.items()):
                if i > 0:
                    code_writer.emit(",\n")

                # Emit constant annotations
                for annotation in constant.annotations:
                    code_writer.emit("\n")
                    annotation.emit(code_writer)

                code_writer.emit(name)

                # If this is an anonymous class
                if constant.anonymous_class_format or constant.fields or constant.methods:
                    # Emit constructor arguments
                    if constant.anonymous_class_format:
                        code_writer.emit("(")
                        code_block = CodeBlock.of(constant.anonymous_class_format, *constant.anonymous_class_args)
                        code_block.emit(code_writer)
                        code_writer.emit(")")

                    # Emit class body
                    code_writer.emit(" {\n")
                    code_writer.indent()

                    # Emit fields
                    for field in constant.fields:
                        field.emit(code_writer)
                        code_writer.emit("\n")

                    # Emit methods
                    for method in constant.methods:
                        method.emit(code_writer)
                        code_writer.emit("\n")

                    code_writer.unindent()
                    code_writer.emit("}")

            if self.fields or self.methods or self.types:
                code_writer.emit(";\n\n")
            else:
                code_writer.emit("\n")

        # Emit fields
        for field in self.fields:
            field.emit(code_writer)

        if self.fields and (self.methods or self.types):
            code_writer.emit("\n")

        # Emit methods
        for i, method in enumerate(self.methods):
            method.emit(code_writer)
            if i < len(self.methods) - 1:
                code_writer.emit("\n")

        if self.methods and self.types:
            code_writer.emit("\n")

        # Emit nested types
        for i, type_spec in enumerate(self.types):
            type_spec.emit(code_writer)
            code_writer.emit("\n")
            if i < len(self.types) - 1:
                code_writer.emit("\n")

        code_writer.unindent()
        code_writer.emit("}")
        self.__unexclude_direct_inner_classes(code_writer)

    def to_builder(self) -> "Builder":
        return TypeSpec.Builder(
            self.name,
            self.kind,
            deep_copy(self.modifiers),
            deep_copy(self.type_variables),
            deep_copy(self.superclass),
            deep_copy(self.superinterfaces),
            deep_copy(self.permitted_subclasses),
            deep_copy(self.javadoc),
            deep_copy(self.annotations),
            deep_copy(self.fields),
            deep_copy(self.methods),
            deep_copy(self.types),
            deep_copy(self.enum_constants),
            deep_copy(self.record_components),
        )

    def __exclude_direct_inner_classes(self, code_writer: "CodeWriter") -> None:
        for type_spec in self.types:
            code_writer.exclude_scoped_class(type_spec.name)

    def __unexclude_direct_inner_classes(self, code_writer: "CodeWriter") -> None:
        for type_spec in self.types:
            code_writer.unexclude_scoped_class(type_spec.name)

    @staticmethod
    def builder(name: str) -> "Builder":
        return TypeSpec.Builder(name, TypeSpec.Kind.CLASS)

    @staticmethod
    def class_builder(name: str) -> "Builder":
        return TypeSpec.Builder(name, TypeSpec.Kind.CLASS)

    @staticmethod
    def interface_builder(name: str) -> "Builder":
        return TypeSpec.Builder(name, TypeSpec.Kind.INTERFACE)

    @staticmethod
    def enum_builder(name: str) -> "Builder":
        return TypeSpec.Builder(name, TypeSpec.Kind.ENUM)

    @staticmethod
    def annotation_builder(name: str) -> "Builder":
        return TypeSpec.Builder(name, TypeSpec.Kind.ANNOTATION)

    @staticmethod
    def record_builder(name: str) -> "Builder":
        return TypeSpec.Builder(name, TypeSpec.Kind.RECORD)

    @staticmethod
    def anonymous_class_builder(format_string: str = "", *args) -> "AnonymousClassBuilder":
        builder = TypeSpec.AnonymousClassBuilder(ClassName.OBJECT)
        if format_string:
            builder.add_super_class_constructor_argument(format_string, *args)
        return builder

    class Builder(Code.Builder["TypeSpec"]):
        """
        Builder for TypeSpec instances.
        """

        # Private fields defined at the top
        __name: str
        __kind: "TypeSpec.Kind"
        __modifiers: set[Modifier]
        __type_variables: list[TypeVariableName]
        __superclass_field: Optional[TypeName]
        __superinterfaces: list[TypeName]
        __permitted_subclasses: list[TypeName]
        __javadoc: Optional[CodeBlock]
        __annotations: list[AnnotationSpec]
        __fields: list[FieldSpec]
        __methods: list[MethodSpec]
        __types: list["TypeSpec"]
        __enum_constants: dict[str, "TypeSpec"]
        __record_components: list[tuple[TypeName, str]]

        def __init__(
            self,
            name: str,
            kind: "TypeSpec.Kind",
            modifiers: Optional[set[Modifier]] = None,
            type_variables: Optional[list[TypeVariableName]] = None,
            superclass: Optional[TypeName] = None,
            superinterfaces: Optional[list[TypeName]] = None,
            permitted_subclasses: Optional[list[TypeName]] = None,
            javadoc: Optional[CodeBlock] = None,
            annotations: Optional[list[AnnotationSpec]] = None,
            fields: Optional[list[FieldSpec]] = None,
            methods: Optional[list[MethodSpec]] = None,
            types: Optional[list["TypeSpec"]] = None,
            enum_constants: Optional[dict[str, "TypeSpec"]] = None,
            record_components: Optional[list[tuple[TypeName, str]]] = None,
        ):
            self.__name = name
            self.__kind = kind
            self.__modifiers = modifiers or set()
            self.__type_variables = type_variables or []
            self.__superclass_field = superclass
            self.__superinterfaces = superinterfaces or []
            self.__permitted_subclasses = permitted_subclasses or []
            self.__javadoc = javadoc
            self.__annotations = annotations or []
            self.__fields = fields or []
            self.__methods = methods or []
            self.__types = types or []
            self.__enum_constants = enum_constants or {}
            self.__record_components = record_components or []

        def add_modifiers(self, *modifiers: Modifier) -> "TypeSpec.Builder":
            self.__modifiers.update(modifiers)
            # Check if modifiers are valid for classes
            Modifier.check_class_modifiers(self.__modifiers)
            return self

        def add_type_variable(self, type_variable: TypeVariableName) -> "TypeSpec.Builder":
            self.__type_variables.append(type_variable)
            return self

        def superclass(self, superclass: Union["TypeName", str, type]) -> "TypeSpec.Builder":
            if self.__kind == TypeSpec.Kind.INTERFACE or self.__kind == TypeSpec.Kind.ANNOTATION:
                raise ValueError("Interfaces and annotations cannot have a superclass")

            if not isinstance(superclass, TypeName):
                superclass = TypeName.get(superclass)

            self.__superclass_field = superclass
            return self

        def add_superinterface(self, superinterface: Union["TypeName", str, type]) -> "TypeSpec.Builder":
            if not isinstance(superinterface, TypeName):
                superinterface = TypeName.get(superinterface)

            self.__superinterfaces.append(superinterface)
            return self

        def add_permitted_subclass(self, subclass: Union["TypeName", str, type]) -> "TypeSpec.Builder":
            if not isinstance(subclass, TypeName):
                subclass = TypeName.get(subclass)

            self.__permitted_subclasses.append(subclass)
            return self

        def add_javadoc(self, format_string: str, *args) -> "TypeSpec.Builder":
            self.__javadoc = CodeBlock.add_javadoc(self.__javadoc, format_string, *args)
            return self

        def add_javadoc_line(self, format_string: str = EMPTY_STRING, *args) -> "TypeSpec.Builder":
            self.__javadoc = CodeBlock.add_javadoc_line(self.__javadoc, format_string, *args)
            return self

        def add_annotation(self, annotation_spec: AnnotationSpec) -> "TypeSpec.Builder":
            self.__annotations.append(annotation_spec)
            return self

        def add_field(self, field_spec: FieldSpec) -> "TypeSpec.Builder":
            self.__fields.append(field_spec)
            return self

        def add_method(self, method_spec: MethodSpec) -> "TypeSpec.Builder":
            # set constructor name to class name
            if method_spec.kind in (MethodSpec.Kind.CONSTRUCTOR, MethodSpec.Kind.COMPACT_CONSTRUCTOR):
                method_spec = method_spec.to_builder().set_name(self.__name).build()

            if self.__kind == TypeSpec.Kind.INTERFACE:
                method_spec = method_spec.to_builder().in_interface().build()

            self.__methods.append(method_spec)
            return self

        def add_type(self, type_spec: "TypeSpec") -> "TypeSpec.Builder":
            self.__types.append(type_spec)
            return self

        def add_enum_constant(self, name: str) -> "TypeSpec.Builder":
            if self.__kind != TypeSpec.Kind.ENUM:
                raise ValueError("Enum constants can only be added to enums")

            # Create a simple enum constant with no body
            self.__enum_constants[name] = TypeSpec(
                "", TypeSpec.Kind.CLASS, set(), [], None, [], [], None, [], [], [], [], {}, []
            )
            return self

        def add_enum_constant_with_class_body(self, name: str, type_spec: "TypeSpec") -> "TypeSpec.Builder":
            if self.__kind != TypeSpec.Kind.ENUM:
                raise ValueError("Enum constants can only be added to enums")

            self.__enum_constants[name] = type_spec
            return self

        def add_record_component(
            self, type_or_param: Union["ParameterSpec", "TypeName", str, type], name: Optional[str] = None
        ) -> "TypeSpec.Builder":
            if self.__kind != TypeSpec.Kind.RECORD:
                raise ValueError("Record components can only be added to records")

            if isinstance(type_or_param, ParameterSpec):
                # Extract type and name from ParameterSpec
                component_type = type_or_param.type_name
                component_name = type_or_param.name
            else:
                # Use provided type and name
                if name is None:
                    raise ValueError("name parameter is required when type_or_param is not a ParameterSpec")
                component_type = (
                    TypeName.get(type_or_param) if not isinstance(type_or_param, TypeName) else type_or_param
                )
                component_name = name

            self.__record_components.append((component_type, component_name))
            return self

        def build(self) -> "TypeSpec":
            # Default superclass for enums
            if self.__kind == TypeSpec.Kind.ENUM and self.__superclass_field is None:
                # For now, just use a simple enum superclass without parameterization
                self.__superclass_field = ClassName.get("java.lang", "Enum")

            return TypeSpec(
                self.__name,
                self.__kind,
                deep_copy(self.__modifiers),
                deep_copy(self.__type_variables),
                deep_copy(self.__superclass_field),
                deep_copy(self.__superinterfaces),
                deep_copy(self.__permitted_subclasses),
                deep_copy(self.__javadoc),
                deep_copy(self.__annotations),
                deep_copy(self.__fields),
                deep_copy(self.__methods),
                deep_copy(self.__types),
                deep_copy(self.__enum_constants),
                deep_copy(self.__record_components),
            )

    class AnonymousClassBuilder(Code.Builder["TypeSpec"]):
        """
        Builder for anonymous inner classes.
        """

        def __init__(self, type_name: TypeName):
            self.type_name = type_name
            self.type_spec_builder = TypeSpec.builder("")
            self.constructor_args_format = ""
            self.constructor_args = []

        def add_super_class_constructor_argument(self, format_string: str, *args) -> "TypeSpec.AnonymousClassBuilder":
            self.constructor_args_format = format_string
            self.constructor_args.extend(args)
            return self

        def add_superinterface(self, superinterface: Union["TypeName", str, type]) -> "TypeSpec.AnonymousClassBuilder":
            """Add a superinterface that this anonymous class implements."""
            if not isinstance(superinterface, TypeName):
                superinterface = TypeName.get(superinterface)
            self.type_name = superinterface
            return self

        def add_method(self, method_spec: MethodSpec) -> "TypeSpec.AnonymousClassBuilder":
            self.type_spec_builder.add_method(method_spec)
            return self

        def add_field(self, field_spec: FieldSpec) -> "TypeSpec.AnonymousClassBuilder":
            self.type_spec_builder.add_field(field_spec)
            return self

        def build(self) -> "TypeSpec":
            type_spec = self.type_spec_builder.build()
            type_spec.anonymous_class_format = self.constructor_args_format
            type_spec.anonymous_class_args = self.constructor_args
            type_spec.superclass = self.type_name
            return type_spec
