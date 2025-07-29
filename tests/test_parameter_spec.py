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

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.parameter_spec import ParameterSpec
from pyjavapoet.type_name import ClassName


class ParameterSpecTest(unittest.TestCase):
    """Test the ParameterSpec class."""

    def test_equals_and_hash_code(self):
        """Test equals and hash code functionality."""
        a = ParameterSpec.builder(ClassName.get("java.lang", "String"), "name").build()
        b = ParameterSpec.builder(ClassName.get("java.lang", "String"), "name").build()
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_basic_parameter_creation(self):
        """Test basic parameter creation."""
        param = ParameterSpec.builder(ClassName.get("java.lang", "String"), "value").build()

        result = str(param)
        self.assertEqual(result, "String value")

    def test_parameter_with_modifiers(self):
        """Test parameter with modifiers."""
        param = ParameterSpec.builder(ClassName.get("java.lang", "String"), "value").add_final().build()

        result = str(param)
        self.assertEqual(result, "final String value")

    def test_parameter_with_annotation(self):
        """Test parameter with annotation."""
        annotation = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
        param = ParameterSpec.builder(ClassName.get("java.lang", "String"), "value").add_annotation(annotation).build()

        result = str(param)
        self.assertIn("@Nullable", result)
        self.assertIn("String value", result)

    def test_parameter_with_multiple_annotations(self):
        """Test parameter with multiple annotations."""
        nullable = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
        nonnull = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nonnull")).build()

        param = (
            ParameterSpec.builder(ClassName.get("java.lang", "String"), "value")
            .add_annotation(nullable)
            .add_annotation(nonnull)
            .build()
        )

        result = str(param)
        self.assertIn("@Nullable", result)
        self.assertIn("@Nonnull", result)

    def test_primitive_parameter(self):
        """Test primitive parameter."""
        param = ParameterSpec.builder("int", "count").build()

        result = str(param)
        self.assertEqual(result, "int count")

    def test_array_parameter(self):
        """Test array parameter."""
        param = ParameterSpec.builder("String[]", "args").build()

        result = str(param)
        self.assertEqual(result, "String[] args")

    def test_varargs_parameter(self):
        """Test varargs parameter."""
        param = ParameterSpec.builder("Object...", "values").build()

        result = str(param)
        self.assertEqual(result, "Object... values")

    def test_generic_parameter(self):
        """Test generic parameter."""
        list_string = ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String"))
        param = ParameterSpec.builder(list_string, "items").build()

        result = str(param)
        self.assertIn("List<String> items", result)

    def test_keyword_name(self):
        """Test that Java keyword names are rejected."""
        with self.assertRaises(ValueError):
            ParameterSpec.builder(ClassName.get("java.lang", "String"), "class")

        with self.assertRaises(ValueError):
            ParameterSpec.builder(ClassName.get("java.lang", "String"), "int")

        with self.assertRaises(ValueError):
            ParameterSpec.builder(ClassName.get("java.lang", "String"), "return")

    def test_parameter_to_builder(self):
        """Test parameter to builder conversion."""
        original = ParameterSpec.builder(ClassName.get("java.lang", "String"), "value").add_final().build()

        annotation = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
        modified = original.to_builder().add_annotation(annotation).build()

        original_str = str(original)
        modified_str = str(modified)

        self.assertNotIn("@Nullable", original_str)
        self.assertIn("@Nullable", modified_str)
        self.assertIn("final", modified_str)

    def test_final_parameter(self):
        """Test final parameter."""
        param = ParameterSpec.builder(ClassName.get("java.lang", "String"), "value").add_final().build()

        result = str(param)
        self.assertEqual(result, "final String value")

    def test_invalid_parameter_name(self):
        """Test that invalid parameter names are rejected."""
        with self.assertRaises(ValueError):
            ParameterSpec.builder(ClassName.get("java.lang", "String"), "")

        with self.assertRaises(ValueError):
            ParameterSpec.builder(ClassName.get("java.lang", "String"), "123invalid")

        with self.assertRaises(ValueError):
            ParameterSpec.builder(ClassName.get("java.lang", "String"), "invalid-name")

    def test_parameter_with_complex_annotation(self):
        """Test parameter with complex annotation."""
        annotation = (
            AnnotationSpec.builder(ClassName.get("com.example", "Validated"))
            .add_member("pattern", "$S", "[a-zA-Z]+")
            .add_member("message", "$S", "Invalid input")
            .build()
        )

        param = ParameterSpec.builder(ClassName.get("java.lang", "String"), "input").add_annotation(annotation).build()

        result = str(param)
        self.assertIn("@Validated", result)
        self.assertIn('pattern = "[a-zA-Z]+"', result)
        self.assertIn('message = "Invalid input"', result)

    def test_receiver_parameter(self):
        """Test receiver parameter (for inner class methods)."""
        # In Java, receiver parameters are written as: OuterClass OuterClass.this
        param = ParameterSpec.builder(ClassName.get("com.example", "OuterClass"), "OuterClass.this").build()
        param2 = ParameterSpec.builder(ClassName.get("com.example", "OuterClass"), "this").build()

        result = str(param)
        self.assertEqual(result, "OuterClass OuterClass.this")
        result2 = str(param2)
        self.assertEqual(result2, "OuterClass this")

    def test_add_final_modifier(self):
        """Test adding final modifier."""
        builder = ParameterSpec.builder(ClassName.get("java.lang", "String"), "value")
        builder.add_final()
        param = builder.build()
        result = str(param)
        self.assertEqual(result, "final String value")

    def test_parameter_builder_from_parameter(self):
        """Test creating builder from existing parameter."""
        param = ParameterSpec.builder(ClassName.get("java.lang", "String"), "name").add_final().build()

        builder = param.to_builder()
        new_param = builder.build()

        self.assertEqual(str(param), str(new_param))

    def test_wildcard_type_parameter(self):
        """Test parameter with wildcard type."""
        wildcard_list = ClassName.get("java.util", "List").with_type_arguments("? extends Number")
        param = ParameterSpec.builder(wildcard_list, "numbers").build()

        result = str(param)
        self.assertIn("List<? extends Number>", result)

    def test_nested_generic_parameter(self):
        """Test parameter with nested generic types."""
        map_type = ClassName.get("java.util", "Map").with_type_arguments(
            ClassName.get("java.lang", "String"),
            ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "Integer")),
        )
        param = ParameterSpec.builder(map_type, "data").build()

        result = str(param)
        self.assertIn("Map<String, List<Integer>>", result)


if __name__ == "__main__":
    unittest.main()
