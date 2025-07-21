"""
Classes representing Java types in PyPoet.

This module defines classes for representing Java types:
- TypeName: Base class for all types
- ClassName: Represents a class or interface type
- ArrayTypeName: Represents an array type
- ParameterizedTypeName: Represents a type with generic arguments
- TypeVariableName: Represents a type variable (generic type parameter)
- WildcardTypeName: Represents a wildcard type (e.g., ? extends Number)
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

from pyjavapoet.util import is_ascii_upper

if TYPE_CHECKING:
    from pyjavapoet.annotation_spec import AnnotationSpec
    from pyjavapoet.code_writer import CodeWriter

JAVA_LANG_PACKAGE = "java.lang"

class TypeName(ABC):
    """
    Base class for types in Java's type system.
    """
    INTEGER: "ClassName"
    LONG: "ClassName"
    DOUBLE: "ClassName"
    FLOAT: "ClassName"
    SHORT: "ClassName"
    BYTE: "ClassName"
    CHARACTER: "ClassName"
    BOOLEAN: "ClassName"
    VOID: "ClassName"
    OBJECT: "ClassName"
    STRING: "ClassName"
    VOID: "ClassName"

    # Primitive types mapping
    PRIMITIVE_TYPES = {
        "boolean": "Boolean",
        "byte": "Byte",
        "short": "Short",
        "int": "Integer",
        "long": "Long",
        "char": "Character",
        "float": "Float",
        "double": "Double",
        "void": "Void",
    }

    BOXED_PRIMITIVE_TYPES = {
        "Boolean",
        "Byte",
        "Character",
        "Double",
        "Float",
        "Integer",
        "Long",
        "Short",
        "Void",
    }

    ALL_PRIMITIVE_TYPES = {
        "Object": JAVA_LANG_PACKAGE,
        "String": JAVA_LANG_PACKAGE,
    } | { 
        t: None for t in PRIMITIVE_TYPES.values() 
    } | {
        t: JAVA_LANG_PACKAGE for t in BOXED_PRIMITIVE_TYPES
    }

    def __init__(self, annotations: list["AnnotationSpec"] = None):
        self.annotations = annotations or []

    @abstractmethod
    def emit(self, code_writer: "CodeWriter") -> None:
        pass

    def annotated(self, *annotations: "AnnotationSpec") -> "TypeName":
        result = self.copy()
        result.annotations.extend(annotations)
        return result

    @abstractmethod
    def copy(self) -> "TypeName":
        pass

    def __str__(self) -> str:
        from pyjavapoet.code_writer import CodeWriter

        writer = CodeWriter()
        self.emit(writer)
        return str(writer)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TypeName):
            return False
        return str(self) == str(other)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def with_type_arguments(self, *type_arguments: "TypeName") -> "ParameterizedTypeName":
        return ParameterizedTypeName.get(self, *type_arguments)
    
    def is_primitive(self) -> bool:
        return (
            isinstance(self, ClassName)
            and not self.package_name
            and self.simple_name in TypeName.PRIMITIVE_TYPES
        )
    
    def is_boxed_primitive(self) -> bool:
        return (
            isinstance(self, ClassName)
            and self.package_name == JAVA_LANG_PACKAGE
            and self.simple_name in TypeName.BOXED_PRIMITIVE_TYPES
        )

    @staticmethod
    def get(type_mirror_or_name: Union[str, type, "TypeName"]) -> "TypeName":
        if isinstance(type_mirror_or_name, TypeName):
            return type_mirror_or_name

        if isinstance(type_mirror_or_name, str):
            # Check if it's a primitive type
            if type_mirror_or_name in TypeName.ALL_PRIMITIVE_TYPES:
                # Create primitive type
                return ClassName.get("", type_mirror_or_name)

            # Parse the string as a fully qualified class name
            return ClassName.get_from_fqcn(type_mirror_or_name)

        # Handle Python types
        if isinstance(type_mirror_or_name, type):
            type_name = type_mirror_or_name.__name__
            # Map Python types to Java types
            type_mapping = {
                "bool": "boolean",
                "int": "int",
                "float": "float",
                "str": "java.lang.String",
                "list": "java.util.List",
                "dict": "java.util.Map",
                "set": "java.util.Set",
                "tuple": "java.util.List",
                "None": "void",
            }

            if type_name in type_mapping:
                return TypeName.get(type_mapping[type_name])
            else:
                # Default to Java Object for other Python types
                return TypeName.OBJECT

class ClassName(TypeName):
    package_name: str
    simple_names: list[str]
    ignore_package_name: bool

    def __init__(self, package_name: str, simple_names: list[str], annotations: list["AnnotationSpec"] = None):
        super().__init__(annotations)
        if not simple_names:
            raise ValueError("simple_names cannot be empty")

        self.package_name = package_name
        self.simple_names = simple_names
        self.ignore_package_name = package_name in TypeName.ALL_PRIMITIVE_TYPES.values()

    def emit(self, code_writer: "CodeWriter") -> None:
        # Emit annotations if any
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit(" ")

        # Emit class name
        code_writer.emit_type(self)

    def copy(self) -> "ClassName":
        return ClassName(self.package_name, self.simple_names.copy(), self.annotations.copy())
    
    def nested_class(self, *simple_names: str) -> "ClassName":
        return ClassName(self.package_name, self.simple_names + list(simple_names))
    
    def peer_class(self, *simple_names: str) -> "ClassName":
        return ClassName(self.package_name, self.simple_names[:-1] + list(simple_names))
    
    def to_type_param(self) -> "TypeName":
        if self.is_primitive():
            return ClassName(self.package_name, [TypeName.PRIMITIVE_TYPES[self.simple_name]])
        return self
    
    @property
    def reflection_name(self) -> str:
        if not self.package_name:
            return "$".join(self.simple_names)
        return self.package_name + "." + "$".join(self.simple_names)
    
    @property
    def enclosing_class_name(self) -> Optional["ClassName"]:
        if len(self.simple_names) == 1:
            return None
        return ClassName(self.package_name, self.simple_names[:-1])
    
    @property
    def top_level_class_name(self) -> "ClassName":
        if not self.package_name:
            return self
        return ClassName(self.package_name, self.simple_names[:-1] or self.simple_names)

    @property
    def simple_name(self) -> str:
        return self.simple_names[-1]

    @property
    def nested_name(self) -> str:
        return ".".join(self.simple_names)

    @property
    def canonical_name(self) -> str:
        if not self.package_name:
            return ".".join(self.simple_names)
        return f"{self.package_name}.{self.nested_name}"
    
    def __str__(self) -> str:
        return self.canonical_name

    @staticmethod
    def get(package_name: str, *simple_names: str) -> "ClassName":
        # Handle nested classes
        all_simple_names = []
        for simple_name in simple_names:
            if "." in simple_name:
                all_simple_names.extend(simple_name.split("."))
            else:
                all_simple_names.append(simple_name)

        if not package_name and len(simple_names) == 1 and simple_names[0] in TypeName.ALL_PRIMITIVE_TYPES:
            package_name = TypeName.ALL_PRIMITIVE_TYPES[simple_names[0]]

        return ClassName(package_name, all_simple_names)

    @staticmethod
    def get_from_fqcn(fully_qualified_class_name: str) -> "ClassName":
        if "." not in fully_qualified_class_name:
            return ClassName.get("", fully_qualified_class_name)

        parts = fully_qualified_class_name.split(".")
        package_parts = []
        class_parts = []

        # Heuristic: assume parts with lowercase first letter are package parts
        for part in parts:
            if class_parts or (part and is_ascii_upper(part[0])):
                class_parts.append(part)
            else:
                package_parts.append(part)

        if class_parts:
            return ClassName.get(".".join(package_parts), *class_parts)
        else:
            return ClassName.get(".".join(package_parts[:-1]), package_parts[-1])


class ArrayTypeName(TypeName):
    """
    Represents an array type.
    """

    def __init__(self, component_type: TypeName, annotations: list["AnnotationSpec"] = None):
        super().__init__(annotations)
        self.component_type = component_type

    def emit(self, code_writer: "CodeWriter") -> None:
        # Emit component type
        self.component_type.emit(code_writer)

        # Emit annotations
        for annotation in self.annotations:
            code_writer.emit(" ")
            annotation.emit(code_writer)

        # Emit array brackets
        code_writer.emit("[]")

    def copy(self) -> "ArrayTypeName":
        return ArrayTypeName(self.component_type.copy(), self.annotations.copy())

    @staticmethod
    def of(component_type: Union["TypeName", str, type]) -> "ArrayTypeName":
        return ArrayTypeName(TypeName.get(component_type))

class ParameterizedTypeName(TypeName):
    """
    Represents a parameterized type like List<String>.
    """

    def __init__(
        self,
        raw_type: ClassName,
        type_arguments: list[TypeName],
        owner_type: Optional["ParameterizedTypeName"] = None,
        annotations: list["AnnotationSpec"] = None,
    ):
        super().__init__(annotations)
        self.raw_type = raw_type
        self.type_arguments = type_arguments
        self.owner_type = owner_type

    def emit(self, code_writer: "CodeWriter") -> None:
        # Emit owner type if present
        if self.owner_type is not None:
            self.owner_type.emit(code_writer)
            code_writer.emit(".")
            code_writer.emit(self.raw_type.simple_names[-1])
        else:
            # Emit raw type
            self.raw_type.emit(code_writer)

        # Emit type arguments
        if self.type_arguments:
            code_writer.emit("<")
            for i, type_argument in enumerate(self.type_arguments):
                if i > 0:
                    code_writer.emit(", ")
                if type_argument.is_primitive() and isinstance(type_argument, ClassName):
                    type_argument = type_argument.to_type_param()

                type_argument.emit(code_writer)
            code_writer.emit(">")

    def copy(self) -> "ParameterizedTypeName":
        return ParameterizedTypeName(
            self.raw_type.copy(),
            [arg.copy() for arg in self.type_arguments],
            self.owner_type.copy() if self.owner_type else None,
            self.annotations.copy(),
        )
    
    def nested_class(self, *simple_names: str) -> "ParameterizedTypeName":
        return ParameterizedTypeName(
            self.raw_type.nested_class(*simple_names),
            self.type_arguments,
            self,
            self.annotations,
        )

    @staticmethod
    def get(
        raw_type: Union["ClassName", str], *type_arguments: Union["TypeName", str, type]
    ) -> "ParameterizedTypeName":
        if isinstance(raw_type, str):
            raw_type = ClassName.get_from_fqcn(raw_type)

        type_args = [TypeName.get(arg) for arg in type_arguments]
        return ParameterizedTypeName(raw_type, type_args)


class TypeVariableName(TypeName):
    """
    Represents a type variable like T in List<T>.
    """

    def __init__(self, name: str, bounds: list[TypeName] = None, annotations: list["AnnotationSpec"] = None):
        super().__init__(annotations)
        self.name = name
        self.bounds = bounds or []

    def emit(self, code_writer: "CodeWriter") -> None:
        # Emit annotations
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit(" ")

        # Emit name
        code_writer.emit(self.name)

        # Emit bounds
        if self.bounds:
            code_writer.emit(" extends ")
            for i, bound in enumerate(self.bounds):
                if i > 0:
                    code_writer.emit(" & ")
                bound.emit(code_writer)

    def copy(self) -> "TypeVariableName":
        return TypeVariableName(self.name, [bound.copy() for bound in self.bounds], self.annotations.copy())

    @staticmethod
    def get(name: str, *bounds: Union["TypeName", str, type]) -> "TypeVariableName":
        return TypeVariableName(name, [TypeName.get(bound) for bound in bounds])


class WildcardTypeName(TypeName):
    """
    Represents a wildcard type like ? extends Number or ? super String.
    """

    def __init__(
        self,
        upper_bounds: list[TypeName] = None,
        lower_bounds: list[TypeName] = None,
        annotations: list["AnnotationSpec"] = None,
    ):
        super().__init__(annotations)
        self.upper_bounds = upper_bounds or [TypeName.OBJECT]
        self.lower_bounds = lower_bounds or []

    def emit(self, code_writer) -> None:
        # Emit annotations
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit(" ")

        # Emit wildcard
        code_writer.emit("?")

        # Emit bounds
        if len(self.upper_bounds) == 1 and TypeName.OBJECT is not None and self.upper_bounds[0] == TypeName.OBJECT:
            # Unbounded wildcard or has lower bounds
            pass
        else:
            # Has upper bounds
            if self.upper_bounds:
                code_writer.emit(" extends ")
                for i, bound in enumerate(self.upper_bounds):
                    if i > 0:
                        code_writer.emit(" & ")
                    bound.emit(code_writer)

        if self.lower_bounds:
            code_writer.emit(" super ")
            for i, bound in enumerate(self.lower_bounds):
                if i > 0:
                    code_writer.emit(" & ")
                bound.emit(code_writer)

    def copy(self) -> "WildcardTypeName":
        return WildcardTypeName(
            [bound.copy() for bound in self.upper_bounds],
            [bound.copy() for bound in self.lower_bounds],
            self.annotations.copy(),
        )

    @staticmethod
    def subtypes_of(*upper_bounds: Union["TypeName", str, type]) -> "WildcardTypeName":
        return WildcardTypeName(upper_bounds=[TypeName.get(bound) for bound in upper_bounds])

    @staticmethod
    def supertypes_of(*lower_bounds: Union["TypeName", str, type]) -> "WildcardTypeName":
        return WildcardTypeName(lower_bounds=[TypeName.get(bound) for bound in lower_bounds])

TypeName.INTEGER = ClassName.get("", "Integer")
TypeName.LONG = ClassName.get("", "Long")
TypeName.DOUBLE = ClassName.get("", "Double")
TypeName.FLOAT = ClassName.get("", "Float")
TypeName.SHORT = ClassName.get("", "Short")
TypeName.BYTE = ClassName.get("", "Byte")
TypeName.CHARACTER = ClassName.get("", "Character")
TypeName.BOOLEAN = ClassName.get("", "Boolean")
TypeName.VOID = ClassName.get("", "Void")
TypeName.OBJECT = ClassName.get("", "Object")
