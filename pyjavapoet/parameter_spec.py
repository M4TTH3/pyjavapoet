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

import re
from typing import TYPE_CHECKING, List, Set, Union

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.code_base import Code
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ArrayTypeName, TypeName, TypeVariableName
from pyjavapoet.util import deep_copy, throw_if_invalid_java_identifier

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
        elif isinstance(self.type_name, TypeVariableName):
            self.type_name.emit_name_only(code_writer)
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
