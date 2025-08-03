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
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName


class FieldSpecTest(unittest.TestCase):
    """Test the FieldSpec class."""

    def test_equals_and_hash_code(self):
        """Test equals and hash code functionality."""
        a = FieldSpec.builder(ClassName.get("java.lang", "String"), "field").build()
        b = FieldSpec.builder(ClassName.get("java.lang", "String"), "field").build()
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_basic_field_creation(self):
        """Test basic field creation."""
        field = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
            .add_modifiers(Modifier.PRIVATE, Modifier.FINAL)
            .build()
        )

        result = str(field)
        self.assertEqual("private final String name;\n", result)

    def test_field_with_initializer(self):
        """Test field with initializer."""
        field = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
            .add_modifiers(Modifier.PRIVATE)
            .initializer("$S", "default")
            .build()
        )

        result = str(field)
        self.assertEqual('private String name = "default";\n', result)

    def test_field_with_annotation(self):
        """Test field with annotation."""
        annotation = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
        field = FieldSpec.builder(ClassName.get("java.lang", "String"), "name").add_annotation(annotation).build()

        result = str(field)
        self.assertEqual("@Nullable\nString name;\n", result)

    def test_static_field(self):
        """Test static field creation."""
        field = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "CONSTANT")
            .add_modifiers(Modifier.PUBLIC, Modifier.STATIC, Modifier.FINAL)
            .initializer("$S", "value")
            .build()
        )

        result = str(field)
        self.assertIn("public static final", result)
        self.assertIn("CONSTANT", result)
        self.assertIn('= "value"', result)

    def test_field_with_javadoc(self):
        """Test field with javadoc."""
        field = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
            .add_javadoc_line("@deprecated Use something else")
            .add_javadoc_line("Use something else")
            .build()
        )

        result = str(field)
        expected = """\
/**
 * @deprecated Use something else
 * Use something else
 */
String name;
"""
        self.assertEqual(expected, result)

    def test_primitive_field(self):
        """Test primitive field creation."""
        field = FieldSpec.builder("int", "count").add_modifiers(Modifier.PRIVATE).initializer("$L", 0).build()

        result = str(field)
        self.assertIn("private int count", result)
        self.assertIn("= 0", result)

    def test_array_field(self):
        """Test array field creation."""
        field = FieldSpec.builder("String[]", "names").add_modifiers(Modifier.PRIVATE).build()

        result = str(field)
        self.assertIn("String[] names", result)

    def test_generic_field(self):
        """Test generic field creation."""
        list_string = ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String"))
        field = (
            FieldSpec.builder(list_string, "items")
            .add_modifiers(Modifier.PRIVATE, Modifier.FINAL)
            .initializer("new $T<>()", ClassName.get("java.util", "ArrayList"))
            .build()
        )

        result = str(field)
        self.assertIn("List<String>", result)
        self.assertIn("items", result)

    def test_field_to_builder(self):
        """Test field to builder conversion."""
        original = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "name").add_modifiers(Modifier.PRIVATE).build()
        )

        modified = original.to_builder().add_modifiers(Modifier.FINAL).build()

        original_str = str(original)
        modified_str = str(modified)

        self.assertNotIn("final", original_str)
        self.assertIn("final", modified_str)
        self.assertIn("private", modified_str)

    def test_field_builder_from_field(self):
        """Test creating builder from existing field."""
        field = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
            .add_modifiers(Modifier.PUBLIC)
            .initializer("$S", "initial")
            .build()
        )

        builder = field.to_builder()
        new_field = builder.build()

        self.assertEqual(str(field), str(new_field))

    def test_multiple_annotations(self):
        """Test field with multiple annotations."""
        nullable = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
        deprecated = AnnotationSpec.builder(ClassName.get("java.lang", "Deprecated")).build()

        field = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
            .add_annotation(nullable)
            .add_annotation(deprecated)
            .build()
        )

        result = str(field)
        self.assertEqual("@Nullable\n@Deprecated\nString name;\n", result)

    def test_invalid_field_name(self):
        """Test that invalid field names are rejected."""
        with self.assertRaises(ValueError):
            FieldSpec.builder(ClassName.get("java.lang", "String"), "")

        with self.assertRaises(ValueError):
            FieldSpec.builder(ClassName.get("java.lang", "String"), "123invalid")

    def test_final_field_without_initializer(self):
        """Test final field without initializer (should be allowed, may be set in constructor)."""
        field = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
            .add_modifiers(Modifier.PRIVATE, Modifier.FINAL)
            .build()
        )

        result = str(field)
        self.assertEqual("private final String name;\n", result)

    def test_complex_initializer(self):
        """Test field with complex initializer."""
        field = (
            FieldSpec.builder(
                ClassName.get("java.util", "Map").with_type_arguments(
                    ClassName.get("java.lang", "String"), ClassName.get("java.lang", "Integer")
                ),
                "map",
            )
            .add_modifiers(Modifier.PRIVATE, Modifier.FINAL)
            .initializer(CodeBlock.builder().add("new $T<>()", ClassName.get("java.util", "HashMap")).build())
            .build()
        )

        result = str(field)
        self.assertEqual("private final Map<String, Integer> map = new HashMap<>();\n", result)


if __name__ == "__main__":
    unittest.main()
