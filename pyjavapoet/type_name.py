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

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

from pyjavapoet.util import deep_copy, is_ascii_upper

if TYPE_CHECKING:
    from pyjavapoet.annotation_spec import AnnotationSpec
    from pyjavapoet.code_writer import CodeWriter

JAVA_LANG_PACKAGE = "java.lang"


class TypeName(ABC):
    """
    Base class for types in Java's type system.
    """

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

    ALL_PRIMITIVE_TYPES = (
        {
            "Object": JAVA_LANG_PACKAGE,
            "String": JAVA_LANG_PACKAGE,
        }
        | {t: "" for t in PRIMITIVE_TYPES.values()}
        | {t: JAVA_LANG_PACKAGE for t in BOXED_PRIMITIVE_TYPES}
    )

    def __init__(self, annotations: list["AnnotationSpec"] | None = None):
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

    def is_primitive(self) -> bool:
        return (
            isinstance(self, ClassName)
            and not self.package_name
            and ClassName.strip_simple_name(self.simple_name) in TypeName.PRIMITIVE_TYPES
        )

    def is_boxed_primitive(self) -> bool:
        return (
            isinstance(self, ClassName)
            and self.package_name == JAVA_LANG_PACKAGE
            and ClassName.strip_simple_name(self.simple_name) in TypeName.BOXED_PRIMITIVE_TYPES
        )

    def is_any_primitive(self) -> bool:
        if not isinstance(self, ClassName):
            return False

        stripped_simple_name = ClassName.strip_simple_name(self.simple_name)
        package_name = TypeName.ALL_PRIMITIVE_TYPES.get(stripped_simple_name)
        if package_name:
            return self.package_name == package_name

        return False

    @staticmethod
    def get(type_mirror_or_name: Union[str, type, "TypeName", None]) -> "TypeName":
        if not type_mirror_or_name:
            return ClassName.VOID

        if isinstance(type_mirror_or_name, TypeName):
            return type_mirror_or_name

        if isinstance(type_mirror_or_name, str):
            # Check if it's a primitive type
            if ClassName.strip_simple_name(type_mirror_or_name) in TypeName.ALL_PRIMITIVE_TYPES:
                # Create primitive type
                return ClassName.get("", type_mirror_or_name)

            # Parse the string as a fully qualified class name
            return ClassName.get_from_fqcn(type_mirror_or_name)

        # Handle Python types
        if isinstance(type_mirror_or_name, type):
            # Map Python types to Java types
            type_mapping = {
                bool: ClassName.BOOLEAN,
                int: ClassName.INTEGER,
                float: ClassName.FLOAT,
                str: ClassName.STRING,
                list: ClassName.LIST,
                dict: ClassName.MAP,
                set: ClassName.SET,
                tuple: ClassName.LIST,
            }

            if type_mirror_or_name in type_mapping:
                return TypeName.get(type_mapping[type_mirror_or_name])
            else:
                # Default to Java Object for other Python types
                return ClassName.OBJECT


class ClassName(TypeName):
    INTEGER: "ClassName"
    LONG: "ClassName"
    DOUBLE: "ClassName"
    FLOAT: "ClassName"
    SHORT: "ClassName"
    BYTE: "ClassName"
    CHAR: "ClassName"
    BOOLEAN: "ClassName"
    VOID: "ClassName"
    OBJECT: "ClassName"
    STRING: "ClassName"
    VOID: "ClassName"
    LIST: "ClassName"
    MAP: "ClassName"
    SET: "ClassName"

    # Commonly used Java library types
    LIST: "ClassName"
    MAP: "ClassName"
    SET: "ClassName"
    COLLECTION: "ClassName"
    ITERABLE: "ClassName"
    ITERATOR: "ClassName"
    OPTIONAL: "ClassName"
    STREAM: "ClassName"
    ARRAY_LIST: "ClassName"
    LINKED_LIST: "ClassName"
    HASH_MAP: "ClassName"
    LINKED_HASH_MAP: "ClassName"
    TREE_MAP: "ClassName"
    HASH_SET: "ClassName"
    LINKED_HASH_SET: "ClassName"
    TREE_SET: "ClassName"
    QUEUE: "ClassName"
    DEQUE: "ClassName"
    STACK: "ClassName"
    VECTOR: "ClassName"
    ENUM_SET: "ClassName"
    ENUM_MAP: "ClassName"
    BIG_DECIMAL: "ClassName"
    BIG_INTEGER: "ClassName"
    DATE: "ClassName"
    CALENDAR: "ClassName"
    LOCALE: "ClassName"
    FILE: "ClassName"
    PATH: "ClassName"
    URL: "ClassName"
    UUID: "ClassName"
    OBJECTS: "ClassName"
    STRING_BUILDER: "ClassName"
    STRING_BUFFER: "ClassName"

    package_name: str
    simple_names: list[str]
    ignore_import: bool

    def __init__(self, package_name: str, simple_names: list[str], annotations: list["AnnotationSpec"] | None = None):
        super().__init__(annotations)
        if not simple_names:
            raise ValueError("simple_names cannot be empty")

        self.package_name = package_name
        self.simple_names = simple_names
        self.ignore_import = package_name == JAVA_LANG_PACKAGE or self.is_any_primitive()

    def emit(self, code_writer: "CodeWriter") -> None:
        # Emit annotations if any
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit(" ")

        # Emit class name
        code_writer.emit_type(self)

    def copy(self) -> "ClassName":
        return ClassName(self.package_name, deep_copy(self.simple_names), deep_copy(self.annotations))

    def nested_class(self, *simple_names: str) -> "ClassName":
        return ClassName(self.package_name, self.simple_names + list(simple_names))

    def peer_class(self, *simple_names: str) -> "ClassName":
        return ClassName(self.package_name, self.simple_names[:-1] + list(simple_names))

    def with_type_arguments(self, *type_arguments: Union["TypeName", str, type]) -> "ParameterizedTypeName":
        return ParameterizedTypeName(self, [TypeName.get(arg) for arg in type_arguments])

    def array(self) -> "ArrayTypeName":
        """Return an array type with this class as the component type."""
        return ArrayTypeName(self)

    def to_type_param(self) -> "TypeName":
        if self.is_primitive():
            boxed_name = TypeName.PRIMITIVE_TYPES[self.simple_name]
            package_name = TypeName.ALL_PRIMITIVE_TYPES[boxed_name]
            return ClassName.get(package_name, boxed_name)
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
    def top_simple_name(self) -> str:
        return self.simple_names[0]

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
    def strip_simple_name(simple_name: str) -> str:
        if simple_name.endswith("[]"):
            return simple_name[:-2]
        elif simple_name.endswith("..."):
            return simple_name[:-3]
        return simple_name

    @staticmethod
    def get(package_name: str, *simple_names: str) -> "ClassName":
        # Handle nested classes
        all_simple_names = []
        for simple_name in simple_names:
            if "." in simple_name:
                all_simple_names.extend(simple_name.split("."))
            else:
                all_simple_names.append(simple_name)

        if not package_name and len(simple_names) == 1:
            stripped_simple_name = ClassName.strip_simple_name(simple_names[0])
            if pkg_name := TypeName.ALL_PRIMITIVE_TYPES.get(stripped_simple_name):
                package_name = pkg_name

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

    def __init__(self, component_type: TypeName, annotations: list["AnnotationSpec"] | None = None):
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
        return ArrayTypeName(deep_copy(self.component_type), deep_copy(self.annotations))

    @staticmethod
    def get(component_type: Union["TypeName", str, type]) -> "ArrayTypeName":
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
        annotations: list["AnnotationSpec"] | None = None,
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

                if isinstance(type_argument, TypeVariableName):
                    type_argument.emit_name_only(code_writer)
                else:
                    type_argument.emit(code_writer)
            code_writer.emit(">")

    def copy(self) -> "ParameterizedTypeName":
        return ParameterizedTypeName(
            deep_copy(self.raw_type),
            deep_copy(self.type_arguments),
            deep_copy(self.owner_type),
            deep_copy(self.annotations),
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

    def __init__(
        self,
        name: str,
        bounds: list[TypeName] | None = None,
        annotations: list["AnnotationSpec"] | None = None,
    ):
        super().__init__(annotations)
        self.name = name
        self.bounds = bounds or []

    def emit(self, code_writer: "CodeWriter") -> None:
        # Emit annotations
        self.emit_name_only(code_writer)

        # Emit bounds
        if self.bounds:
            code_writer.emit(" extends ")
            for i, bound in enumerate(self.bounds):
                if i > 0:
                    code_writer.emit(" & ")
                bound.emit(code_writer)

    def emit_name_only(self, code_writer: "CodeWriter") -> None:
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit(" ")

        # Emit name
        code_writer.emit(self.name)

    def copy(self) -> "TypeVariableName":
        return TypeVariableName(self.name, deep_copy(self.bounds), deep_copy(self.annotations))

    @staticmethod
    def get(name: str, *bounds: Union["TypeName", str, type]) -> "TypeVariableName":
        return TypeVariableName(name, [TypeName.get(bound) for bound in bounds])


class WildcardTypeName(TypeName):
    """
    Represents a wildcard type like ? extends Number or ? super String.
    """

    def __init__(
        self,
        upper_bounds: list[TypeName] | None = None,
        lower_bounds: list[TypeName] | None = None,
        annotations: list["AnnotationSpec"] | None = None,
    ):
        super().__init__(annotations)
        self.upper_bounds = upper_bounds or [ClassName.OBJECT]
        self.lower_bounds = lower_bounds or []

    def emit(self, code_writer) -> None:
        # Emit annotations
        for annotation in self.annotations:
            annotation.emit(code_writer)
            code_writer.emit(" ")

        # Emit wildcard
        code_writer.emit("?")

        # Emit bounds
        if len(self.upper_bounds) == 1 and ClassName.OBJECT is not None and self.upper_bounds[0] == ClassName.OBJECT:
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
            deep_copy(self.upper_bounds),
            deep_copy(self.lower_bounds),
            deep_copy(self.annotations),
        )

    @staticmethod
    def subtypes_of(*upper_bounds: Union["TypeName", str, type]) -> "WildcardTypeName":
        return WildcardTypeName(upper_bounds=[TypeName.get(bound) for bound in upper_bounds])

    @staticmethod
    def supertypes_of(*lower_bounds: Union["TypeName", str, type]) -> "WildcardTypeName":
        return WildcardTypeName(lower_bounds=[TypeName.get(bound) for bound in lower_bounds])


ClassName.INTEGER = ClassName.get("", "int")
ClassName.LONG = ClassName.get("", "long")
ClassName.DOUBLE = ClassName.get("", "double")
ClassName.FLOAT = ClassName.get("", "float")
ClassName.SHORT = ClassName.get("", "short")
ClassName.BYTE = ClassName.get("", "byte")
ClassName.CHAR = ClassName.get("", "char")
ClassName.BOOLEAN = ClassName.get("", "boolean")
ClassName.VOID = ClassName.get("", "void")
ClassName.OBJECT = ClassName.get("java.lang", "Object")
ClassName.STRING = ClassName.get("java.lang", "String")
ClassName.LIST = ClassName.get("java.util", "List")
ClassName.MAP = ClassName.get("java.util", "Map")
ClassName.SET = ClassName.get("java.util", "Set")
ClassName.COLLECTION = ClassName.get("java.util", "Collection")
ClassName.ITERABLE = ClassName.get("java.lang", "Iterable")
ClassName.ITERATOR = ClassName.get("java.util", "Iterator")
ClassName.OPTIONAL = ClassName.get("java.util", "Optional")
ClassName.STREAM = ClassName.get("java.util.stream", "Stream")
ClassName.ARRAY_LIST = ClassName.get("java.util", "ArrayList")
ClassName.LINKED_LIST = ClassName.get("java.util", "LinkedList")
ClassName.HASH_MAP = ClassName.get("java.util", "HashMap")
ClassName.LINKED_HASH_MAP = ClassName.get("java.util", "LinkedHashMap")
ClassName.TREE_MAP = ClassName.get("java.util", "TreeMap")
ClassName.HASH_SET = ClassName.get("java.util", "HashSet")
ClassName.LINKED_HASH_SET = ClassName.get("java.util", "LinkedHashSet")
ClassName.TREE_SET = ClassName.get("java.util", "TreeSet")
ClassName.QUEUE = ClassName.get("java.util", "Queue")
ClassName.DEQUE = ClassName.get("java.util", "Deque")
ClassName.STACK = ClassName.get("java.util", "Stack")
ClassName.VECTOR = ClassName.get("java.util", "Vector")
ClassName.ENUM_SET = ClassName.get("java.util", "EnumSet")
ClassName.ENUM_MAP = ClassName.get("java.util", "EnumMap")
ClassName.BIG_DECIMAL = ClassName.get("java.math", "BigDecimal")
ClassName.BIG_INTEGER = ClassName.get("java.math", "BigInteger")
ClassName.DATE = ClassName.get("java.util", "Date")
ClassName.CALENDAR = ClassName.get("java.util", "Calendar")
ClassName.LOCALE = ClassName.get("java.util", "Locale")
ClassName.FILE = ClassName.get("java.io", "File")
ClassName.PATH = ClassName.get("java.nio.file", "Path")
ClassName.URL = ClassName.get("java.net", "URL")
ClassName.UUID = ClassName.get("java.util", "UUID")
ClassName.OBJECTS = ClassName.get("java.util", "Objects")
ClassName.STRING_BUILDER = ClassName.get("java.lang", "StringBuilder")
ClassName.STRING_BUFFER = ClassName.get("java.lang", "StringBuffer")
