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

from typing import Any, Union

from pyjavapoet.code_base import Code
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.code_writer import CodeWriter
from pyjavapoet.type_name import TypeName
from pyjavapoet.util import deep_copy, throw_if_invalid_java_identifier


class AnnotationSpec(Code["AnnotationSpec"]):
    """
    AnnotationSpec for representing Java annotations.

    This module defines the AnnotationSpec class, which is used to represent
    Java annotations for classes, methods, fields, parameters, etc.
    """

    type_name: "TypeName"
    members: dict[str, list[CodeBlock]]

    def __init__(self, type_name: "TypeName", members: dict[str, list[CodeBlock]]):
        self.type_name = type_name
        self.members = members

    def emit(self, code_writer: "CodeWriter") -> None:
        code_writer.emit("@")
        self.type_name.emit(code_writer)

        if not self.members:
            return

        code_writer.emit("(")

        # For single member annotations with property "value", we can omit the property name
        if len(self.members) == 1 and "value" in self.members:
            for value in self.members["value"]:
                value.emit(code_writer)
        else:
            first = True
            for name, values in self.members.items():
                if not first:
                    code_writer.emit(", ")
                first = False

                code_writer.emit(name)
                code_writer.emit(" = ")

                # Handle array values
                if len(values) > 1:
                    code_writer.emit("{")
                    for i, value in enumerate(values):
                        if i > 0:
                            code_writer.emit(", ")
                        value.emit(code_writer)
                    code_writer.emit("}")
                else:
                    # Single value
                    values[0].emit(code_writer)

        code_writer.emit(")")

    def to_builder(self) -> "Builder":
        return AnnotationSpec.Builder(deep_copy(self.type_name), deep_copy(self.members))

    @staticmethod
    def get(type_name: Union["TypeName", str, type]) -> "AnnotationSpec":
        return AnnotationSpec.builder(type_name).build()

    @staticmethod
    def builder(type_name: Union["TypeName", str, type]) -> "Builder":
        return AnnotationSpec.Builder(TypeName.get(type_name))

    class Builder(Code.Builder["AnnotationSpec"]):
        """
        Builder for AnnotationSpec instances.
        """

        __type_name: "TypeName"
        __members: dict[str, list[CodeBlock]]

        def __init__(self, type_name: "TypeName", members: dict[str, list[CodeBlock]] | None = None):
            self.__type_name = type_name
            self.__members = members or {}  # property name -> list of values

        def add_member(self, name: str, format_string: str, *args: Any) -> "AnnotationSpec.Builder":
            throw_if_invalid_java_identifier(name)
            code_block = CodeBlock.of(format_string, *args)

            if name not in self.__members:
                self.__members[name] = []

            self.__members[name].append(code_block)
            return self

        def build(self) -> "AnnotationSpec":
            # Create a deep copy of members
            return AnnotationSpec(deep_copy(self.__type_name), deep_copy(self.__members))
