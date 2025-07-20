"""
TypeSpec for representing Java classes, interfaces, enums, and annotations.

This module defines the TypeSpec class, which is used to represent Java types:
- Classes
- Interfaces
- Enums
- Annotations
- Records
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName, TypeName, TypeVariableName


class TypeSpec:
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

    class AnonymousClassBuilder:
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

    def __init__(
        self,
        name: str,
        kind: "TypeSpec.Kind",
        modifiers: Set[Modifier],
        type_variables: List[TypeVariableName],
        superclass: Optional[TypeName],
        superinterfaces: List[TypeName],
        permitted_subclasses: List[TypeName],
        javadoc: Optional[CodeBlock],
        annotations: List[AnnotationSpec],
        fields: List[FieldSpec],
        methods: List[MethodSpec],
        types: List["TypeSpec"],
        enum_constants: Dict[str, "TypeSpec"],
        record_components: List[Tuple[TypeName, str]],
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

    def emit(self, code_writer) -> None:
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
        code_writer.indent_more()

        # Emit enum constants
        if self.kind == TypeSpec.Kind.ENUM and self.enum_constants:
            for i, (name, constant) in enumerate(self.enum_constants.items()):
                if i > 0:
                    code_writer.emit(",\n")

                # Emit constant annotations
                for annotation in constant.annotations:
                    code_writer.emit("\n")
                    annotation.emit(code_writer)

                code_writer.emit("\n")
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
                    code_writer.indent_more()

                    # Emit fields
                    for field in constant.fields:
                        field.emit(code_writer)
                        code_writer.emit("\n")

                    # Emit methods
                    for method in constant.methods:
                        method.emit(code_writer)
                        code_writer.emit("\n")

                    code_writer.indent_less()
                    code_writer.emit("}")

            if self.fields or self.methods or self.types:
                code_writer.emit(";\n\n")
            else:
                code_writer.emit("\n")

        # Emit fields
        for field in self.fields:
            field.emit(code_writer)
            code_writer.emit("\n")

        if self.fields and (self.methods or self.types):
            code_writer.emit("\n")

        # Emit methods
        for method in self.methods:
            method.emit(code_writer)
            code_writer.emit("\n")

        if self.methods and self.types:
            code_writer.emit("\n")

        # Emit nested types
        for type_spec in self.types:
            type_spec.emit(code_writer)
            code_writer.emit("\n")

        code_writer.indent_less()
        code_writer.emit("}")

    def __str__(self) -> str:
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)

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
    def anonymous_class_builder(format_string: str, *args) -> "AnonymousClassBuilder":
        from pyjavapoet.type_name import TypeName

        builder = TypeSpec.AnonymousClassBuilder(TypeName.OBJECT)
        if format_string:
            builder.add_super_class_constructor_argument(format_string, *args)
        return builder

    class Builder:
        """
        Builder for TypeSpec instances.
        """

        def __init__(self, name: str, kind: "TypeSpec.Kind"):
            self.name = name
            self.kind = kind
            self.modifiers = set()
            self.type_variables = []
            self.superclass = None
            self.superinterfaces = []
            self.permitted_subclasses = []
            self.javadoc = None
            self.annotations = []
            self.fields = []
            self.methods = []
            self.types = []
            self.enum_constants = {}
            self.record_components = []

        def add_modifiers(self, *modifiers: Modifier) -> "TypeSpec.Builder":
            self.modifiers.update(modifiers)
            # Check if modifiers are valid for classes
            Modifier.check_class_modifiers(self.modifiers)
            return self

        def add_type_variable(self, type_variable: TypeVariableName) -> "TypeSpec.Builder":
            self.type_variables.append(type_variable)
            return self

        def superclass(self, superclass: Union["TypeName", str, type]) -> "TypeSpec.Builder":
            if self.kind == TypeSpec.Kind.INTERFACE or self.kind == TypeSpec.Kind.ANNOTATION:
                raise ValueError("Interfaces and annotations cannot have a superclass")

            if not isinstance(superclass, TypeName):
                superclass = TypeName.get(superclass)

            self.superclass = superclass
            return self

        def add_superinterface(self, superinterface: Union["TypeName", str, type]) -> "TypeSpec.Builder":
            if not isinstance(superinterface, TypeName):
                superinterface = TypeName.get(superinterface)

            self.superinterfaces.append(superinterface)
            return self

        def add_permitted_subclass(self, subclass: Union["TypeName", str, type]) -> "TypeSpec.Builder":
            if not isinstance(subclass, TypeName):
                subclass = TypeName.get(subclass)

            self.permitted_subclasses.append(subclass)
            return self

        def add_javadoc(self, format_string: str, *args) -> "TypeSpec.Builder":
            self.javadoc = CodeBlock.of(format_string, *args)
            return self

        def add_annotation(self, annotation_spec: AnnotationSpec) -> "TypeSpec.Builder":
            self.annotations.append(annotation_spec)
            return self

        def add_field(self, field_spec: FieldSpec) -> "TypeSpec.Builder":
            self.fields.append(field_spec)
            return self

        def add_method(self, method_spec: MethodSpec) -> "TypeSpec.Builder":
            # Set constructor name to class name
            if (
                method_spec.kind == MethodSpec.Kind.CONSTRUCTOR
                or method_spec.kind == MethodSpec.Kind.COMPACT_CONSTRUCTOR
            ):
                if not method_spec.name:
                    # We need to create a new MethodSpec with the correct name
                    from copy import copy

                    new_method = copy(method_spec)
                    new_method.name = self.name
                    method_spec = new_method

            self.methods.append(method_spec)
            return self

        def add_type(self, type_spec: "TypeSpec") -> "TypeSpec.Builder":
            self.types.append(type_spec)
            return self

        def add_enum_constant(self, name: str) -> "TypeSpec.Builder":
            if self.kind != TypeSpec.Kind.ENUM:
                raise ValueError("Enum constants can only be added to enums")

            # Create a simple enum constant with no body
            self.enum_constants[name] = TypeSpec(
                "", TypeSpec.Kind.CLASS, set(), [], None, [], [], None, [], [], [], [], {}, []
            )
            return self

        def add_enum_constant_with_class_body(self, name: str, type_spec: "TypeSpec") -> "TypeSpec.Builder":
            if self.kind != TypeSpec.Kind.ENUM:
                raise ValueError("Enum constants can only be added to enums")

            self.enum_constants[name] = type_spec
            return self

        def add_record_component(self, type_name: Union["TypeName", str, type], name: str) -> "TypeSpec.Builder":
            if self.kind != TypeSpec.Kind.RECORD:
                raise ValueError("Record components can only be added to records")

            if not isinstance(type_name, TypeName):
                type_name = TypeName.get(type_name)

            self.record_components.append((type_name, name))
            return self

        def build(self) -> "TypeSpec":
            # Default superclass for enums
            if self.kind == TypeSpec.Kind.ENUM and self.superclass is None:
                self.superclass = ClassName.get("java.lang", "Enum").parameterized(ClassName.get("", self.name))

            return TypeSpec(
                self.name,
                self.kind,
                self.modifiers.copy(),
                self.type_variables.copy(),
                self.superclass,
                self.superinterfaces.copy(),
                self.permitted_subclasses.copy(),
                self.javadoc,
                self.annotations.copy(),
                self.fields.copy(),
                self.methods.copy(),
                self.types.copy(),
                self.enum_constants.copy(),
                self.record_components.copy(),
            )
