"""
Copyright (C) 2025 Matthew Au-Yeung.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from io import StringIO

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName, ParameterizedTypeName, TypeName, TypeVariableName
from pyjavapoet.type_spec import TypeSpec


class ComplexTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_complex_example(self):
        """Generate a DataProcessor Java class and print it to stdout."""
        # Create type variables
        t = TypeVariableName.get("T")
        r = TypeVariableName.get("R")

        # Define classes we'll use
        list_class = ClassName.get("java.util", "List")
        array_list_class = ClassName.get("java.util", "ArrayList")
        objects_class = ClassName.get("java.util", "Objects")
        override_annotation = ClassName.get("java.lang", "Override")

        # Create a field for the processor name
        name_field = FieldSpec.builder(ClassName.STRING, "name").add_modifiers(Modifier.PRIVATE, Modifier.FINAL).build()

        # Create a counter field
        counter_field = (
            FieldSpec.builder(TypeName.get("int"), "processCount")
            .add_modifiers(Modifier.PRIVATE)
            .initializer("0")
            .build()
        )

        # Create a constructor
        constructor = (
            MethodSpec.constructor_builder()
            .add_modifiers(Modifier.PUBLIC)
            .add_parameter(ClassName.STRING, "name")
            .add_statement("this.$N = $T.requireNonNull($N)", "name", objects_class, "name")
            .build()
        )

        function_class = ParameterizedTypeName.get(ClassName.get("java.util.function", "Function"), t, r)

        # Create a process method
        process_method = (
            MethodSpec.method_builder("process")
            .add_modifiers(Modifier.PUBLIC)
            .add_type_variable(t)
            .add_type_variable(r)
            .returns(ParameterizedTypeName.get(list_class, r))
            .add_parameter(ParameterizedTypeName.get(list_class, t), "input")
            .add_parameter(function_class, "transformer")
            .add_statement("$T<$T> result = new $T<>()", list_class, r, array_list_class)
            .begin_control_flow("for ($T item : input)", t)
            .add_statement("result.add(transformer.apply(item))")
            .end_control_flow()
            .add_statement("processCount++")
            .add_statement("return result")
            .build()
        )

        # Create a toString method with @Override annotation
        to_string = (
            MethodSpec.method_builder("toString")
            .add_annotation(AnnotationSpec.get(override_annotation))
            .add_modifiers(Modifier.PUBLIC)
            .returns(ClassName.STRING)
            .add_statement("return $S + name + $S + processCount + $S", "DataProcessor{name='", "', processCount=", "}")
            .build()
        )

        # Create the DataProcessor class
        processor = (
            TypeSpec.class_builder("DataProcessor")
            .add_modifiers(Modifier.PUBLIC)
            .add_field(name_field)
            .add_field(counter_field)
            .add_method(constructor)
            .add_method(process_method)
            .add_method(to_string)
            .build()
        )

        # Create the Java file
        java_file = (
            JavaFile.builder("com.example.processor", processor)
            .add_file_comment_line("This is a generated file. Do not edit!")
            .build()
        )

        # Print the Java file to stdout
        out = StringIO()
        java_file.write_to(out)
        self.assertEqual(
            out.getvalue(),
            """\
/**
 * This is a generated file. Do not edit!
 */
package com.example.processor;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Function;

public class DataProcessor {
  private final String name;
  private int processCount = 0;

  public DataProcessor(String name) {
    this.name = Objects.requireNonNull(name);
  }

  public <T, R> List<R> process(List<T> input, Function<T, R> transformer) {
    List<R> result = new ArrayList<>();
    for (T item : input) {
      result.add(transformer.apply(item));
    }
    processCount++;
    return result;
  }

  @Override
  public String toString() {
    return "DataProcessor{name='" + name + "', processCount=" + processCount + "}";
  }
}
""",
        )
